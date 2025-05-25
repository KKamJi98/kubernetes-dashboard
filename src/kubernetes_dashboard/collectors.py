"""Parallel data collection from multiple clusters."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from kubernetes_dashboard.kube_client import api_for
from kubernetes_dashboard.quantity import cpu_to_cores, mem_to_bytes


# ------------------- Single cluster functions ------------------- #
def _get_all_pods(ctx: str) -> list:
    """모든 Pod 목록을 반환합니다."""
    core, _ = api_for(ctx)
    return core.list_pod_for_all_namespaces(watch=False).items


def _non_running_pods_list(ctx: str) -> list[dict]:
    """Non-running pods 목록을 반환합니다."""
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
    """Non-running pods 개수를 반환합니다."""
    return len(_non_running_pods_list(ctx))


def _total_pods(ctx: str) -> int:
    """전체 Pod 개수를 반환합니다."""
    return len(_get_all_pods(ctx))


def _node_metrics(ctx: str) -> list[dict]:
    _, cust = api_for(ctx)
    res = cust.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    rows = []
    for n in res["items"]:
        rows.append(
            {
                "cluster": ctx,
                "node": n["metadata"]["name"],
                "cpu": cpu_to_cores(n["usage"]["cpu"]),
                "mem": mem_to_bytes(n["usage"]["memory"]),
            }
        )
    return rows


def _recent_restarts(ctx: str) -> list[dict]:
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
    with ThreadPoolExecutor() as pool:
        non_running_lists = list(pool.map(_non_running_pods_list, selected))
        non_running = [len(nr_list) for nr_list in non_running_lists]
        total_pods = list(pool.map(_total_pods, selected))
        nodes = sum(pool.map(_node_metrics, selected), [])
        restarts = sum(pool.map(_recent_restarts, selected), [])

    return {
        "total_pods": sum(total_pods),
        "non_running_total": sum(non_running),
        "non_running_pods": sum(non_running_lists, []),
        "node_metrics": nodes,
        "recent_restarts": restarts,
    }
