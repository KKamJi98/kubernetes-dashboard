"""Parallel data collection from multiple clusters.

이 모듈은 여러 Kubernetes 클러스터에서 병렬로 데이터를 수집하는 기능을 제공합니다.
ThreadPoolExecutor를 사용하여 여러 클러스터에서 동시에 데이터를 수집하고,
수집된 데이터를 통합하여 대시보드에 표시할 수 있는 형태로 반환합니다.

주요 기능:
- Pod 상태 및 메트릭 수집
- 노드 리소스 사용량 수집
- Pod 로그 수집
- 클러스터 이벤트 수집
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from kubernetes.client.exceptions import ApiException

from kubernetes_dashboard.kube_client import api_for
from kubernetes_dashboard.quantity import cpu_to_cores, mem_to_bytes


# ------------------- Single cluster functions ------------------- #
def _get_all_pods(ctx: str) -> list:
    """모든 Pod 목록을 반환합니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름

    Returns:
        list: Pod 객체 목록
    """
    core, _ = api_for(ctx)
    return core.list_pod_for_all_namespaces(watch=False).items


def _non_running_pods_list(ctx: str) -> list[dict]:
    """Non-running pods 목록을 반환합니다.

    Running 상태가 아닌 모든 Pod의 정보를 수집합니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름

    Returns:
        list[dict]: Non-running Pod 정보 목록 (cluster, pod, ns, node, phase, reason 포함)
    """
    pods = _get_all_pods(ctx)
    result = []
    for p in pods:
        if p.status.phase != "Running":
            result.append(
                {
                    "cluster": ctx,
                    "pod": p.metadata.name,
                    "ns": p.metadata.namespace,
                    "node": p.spec.node_name or "N/A",
                    "phase": p.status.phase,
                    "reason": p.status.reason or "N/A",
                }
            )
    return result


def _non_running_pods(ctx: str) -> int:
    """Non-running pods 개수를 반환합니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름

    Returns:
        int: Running 상태가 아닌 Pod의 개수
    """
    return len(_non_running_pods_list(ctx))


def _total_pods(ctx: str) -> int:
    """전체 Pod 개수를 반환합니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름

    Returns:
        int: 클러스터 내 모든 Pod의 개수
    """
    return len(_get_all_pods(ctx))


def _node_metrics(ctx: str) -> list[dict]:
    """노드 메트릭을 수집합니다. metrics-server가 없으면 빈 리스트를 반환합니다.

    metrics.k8s.io API를 통해 노드의 CPU 및 메모리 사용량을 수집합니다.
    metrics-server가 설치되지 않은 경우에는 노드 목록만 반환하고 메트릭은 'N/A'로 표시합니다.
    노드의 총 용량 대비 현재 사용량을 퍼센트(%)로 계산합니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름

    Returns:
        list[dict]: 노드 메트릭 정보 목록 (cluster, node, cpu, mem, cpu_percent, mem_percent 포함)

    Raises:
        ApiException: metrics-server API 호출 중 404 이외의 오류가 발생한 경우
    """
    try:
        core, cust = api_for(ctx)
        # 노드 용량 정보 가져오기
        nodes = core.list_node().items
        node_capacities = {}
        for node in nodes:
            node_name = node.metadata.name
            node_capacities[node_name] = {
                "cpu": cpu_to_cores(node.status.capacity["cpu"]),
                "mem": mem_to_bytes(node.status.capacity["memory"]),
            }

        # 노드 사용량 정보 가져오기
        res = cust.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
        rows = []
        for n in res["items"]:
            node_name = n["metadata"]["name"]
            cpu_usage = cpu_to_cores(n["usage"]["cpu"])
            mem_usage = mem_to_bytes(n["usage"]["memory"])

            # 용량 대비 사용량 퍼센트 계산
            cpu_percent = "N/A"
            mem_percent = "N/A"

            if node_name in node_capacities:
                cpu_capacity = node_capacities[node_name]["cpu"]
                mem_capacity = node_capacities[node_name]["mem"]

                if cpu_capacity > 0:
                    cpu_percent = (cpu_usage / cpu_capacity) * 100

                if mem_capacity > 0:
                    mem_percent = (mem_usage / mem_capacity) * 100

            rows.append(
                {
                    "cluster": ctx,
                    "node": node_name,
                    "cpu": cpu_usage,
                    "mem": mem_usage,
                    "cpu_percent": cpu_percent,
                    "mem_percent": mem_percent,
                }
            )
        return rows
    except ApiException as e:
        if e.status == 404:
            # metrics-server가 설치되지 않은 경우
            print(
                f"Warning: metrics-server not found in cluster '{ctx}'. "
                f"Node metrics will not be available."
            )
            # 노드 목록은 가져오되 메트릭은 N/A로 설정
            core, _ = api_for(ctx)
            nodes = core.list_node().items
            return [
                {
                    "cluster": ctx,
                    "node": n.metadata.name,
                    "cpu": "N/A",
                    "mem": "N/A",
                    "cpu_percent": "N/A",
                    "mem_percent": "N/A",
                }
                for n in nodes
            ]
        else:
            # 다른 API 오류는 다시 발생시킴
            raise


def _recent_restarts(ctx: str) -> list[dict]:
    """최근 1시간 내에 재시작된 Pod 목록을 반환합니다.

    컨테이너의 마지막 종료 시간을 확인하여 최근 1시간 내에 재시작된 Pod를 식별합니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름

    Returns:
        list[dict]: 최근 재시작된 Pod 정보 목록 (cluster, pod, ns, node, restarts 포함)
    """
    core, _ = api_for(ctx)
    now = datetime.now(timezone.utc)
    pods = core.list_pod_for_all_namespaces(watch=False).items
    out = []
    for p in pods:
        for cs in p.status.container_statuses or []:
            term = cs.last_state.terminated
            if (
                term
                and term.finished_at
                and (now - term.finished_at) <= timedelta(hours=1)
            ):
                out.append(
                    {
                        "cluster": ctx,
                        "pod": p.metadata.name,
                        "ns": p.metadata.namespace,
                        "node": p.spec.node_name,
                        "restarts": cs.restart_count,
                    }
                )
                break
    return out


# ------------------- Multi-cluster integration entry point ------------------- #
def collect(selected: tuple[str, ...]):
    """여러 클러스터에서 데이터를 병렬로 수집하여 통합합니다.

    ThreadPoolExecutor를 사용하여 선택된 모든 클러스터에서 동시에 데이터를 수집합니다.

    Args:
        selected (tuple[str, ...]): 데이터를 수집할 Kubernetes 컨텍스트 이름 튜플

    Returns:
        dict: 다음 키를 포함하는 통합된 데이터 딕셔너리
            - total_pods: 모든 클러스터의 총 Pod 개수
            - non_running_total: 모든 클러스터의 non-running Pod 개수
            - non_running_pods: 모든 클러스터의 non-running Pod 정보 목록
            - node_metrics: 모든 클러스터의 노드 메트릭 정보 목록
            - recent_restarts: 모든 클러스터의 최근 재시작된 Pod 정보 목록
            - events: 모든 클러스터의 최근 이벤트 정보 목록
    """
    with ThreadPoolExecutor() as pool:
        non_running_lists = list(pool.map(_non_running_pods_list, selected))
        non_running = [len(nr_list) for nr_list in non_running_lists]
        total_pods = list(pool.map(_total_pods, selected))
        nodes = sum(pool.map(_node_metrics, selected), [])
        restarts = sum(pool.map(_recent_restarts, selected), [])
        events = sum([_get_cluster_events(ctx) for ctx in selected], [])

    return {
        "total_pods": sum(total_pods),
        "non_running_total": sum(non_running),
        "non_running_pods": sum(non_running_lists, []),
        "node_metrics": nodes,
        "recent_restarts": restarts,
        "events": events,
    }
def _get_pod_logs(ctx: str, pod_name: str, namespace: str, container: str = None, tail_lines: int = 100) -> str:
    """특정 Pod의 로그를 가져옵니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름
        pod_name (str): Pod 이름
        namespace (str): Pod가 위치한 네임스페이스
        container (str, optional): 컨테이너 이름. 기본값은 None (첫 번째 컨테이너)
        tail_lines (int, optional): 가져올 로그 라인 수. 기본값은 100

    Returns:
        str: Pod 로그 문자열
    """
    core, _ = api_for(ctx)
    try:
        return core.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines
        )
    except ApiException as e:
        return f"Error retrieving logs: {e}"


def _get_cluster_events(ctx: str, namespace: str = None, limit: int = 100) -> list[dict]:
    """클러스터 이벤트를 가져옵니다.

    Args:
        ctx (str): Kubernetes 컨텍스트 이름
        namespace (str, optional): 특정 네임스페이스의 이벤트만 가져올 경우. 기본값은 None (모든 네임스페이스)
        limit (int, optional): 가져올 이벤트 수. 기본값은 100

    Returns:
        list[dict]: 이벤트 정보 목록 (cluster, type, reason, object, message, time 포함)
    """
    core, _ = api_for(ctx)
    try:
        if namespace:
            events = core.list_namespaced_event(namespace=namespace, limit=limit)
        else:
            events = core.list_event_for_all_namespaces(limit=limit)
            
        result = []
        for event in events.items:
            result.append({
                "cluster": ctx,
                "type": event.type,
                "reason": event.reason,
                "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                "message": event.message,
                "time": event.last_timestamp or event.event_time,
            })
        
        # 시간 기준 내림차순 정렬
        result.sort(key=lambda x: x["time"] if x["time"] else datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return result
    except ApiException as e:
        print(f"Error retrieving events from cluster {ctx}: {e}")
        return []
