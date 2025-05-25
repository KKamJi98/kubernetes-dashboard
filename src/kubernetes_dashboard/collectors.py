"""Parallel data collection from multiple Kubernetes clusters.

This module provides functions to collect and aggregate data from multiple Kubernetes clusters.
It uses ThreadPoolExecutor for parallel data collection to improve performance when
monitoring multiple clusters simultaneously.

The module is organized into:
1. Single-cluster collection functions (prefixed with _)
2. Multi-cluster aggregation function (collect)

Each single-cluster function focuses on collecting a specific type of data:
- Pod information (total, non-running)
- Node metrics (CPU, memory usage)
- Pod restart information
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from kubernetes_dashboard.kube_client import api_for
from kubernetes_dashboard.quantity import cpu_to_cores, mem_to_bytes


# ------------------- Single cluster functions ------------------- #
def _get_all_pods(ctx: str) -> list:
    """Get all pods from a specific cluster.
    
    Args:
        ctx: Kubernetes context name
        
    Returns:
        List of Pod objects from the Kubernetes API
    """
    core, _ = api_for(ctx)
    return core.list_pod_for_all_namespaces(watch=False).items


def _non_running_pods_list(ctx: str) -> list[dict]:
    """Get a list of pods that are not in 'Running' phase.
    
    This function identifies pods that might need attention because they're
    in states like Pending, Failed, Unknown, etc.
    
    Args:
        ctx: Kubernetes context name
        
    Returns:
        List of dictionaries with information about non-running pods
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
    """Count the number of pods that are not in 'Running' phase.
    
    Args:
        ctx: Kubernetes context name
        
    Returns:
        Count of non-running pods
    """
    return len(_non_running_pods_list(ctx))


def _total_pods(ctx: str) -> int:
    """Count the total number of pods in the cluster.
    
    Args:
        ctx: Kubernetes context name
        
    Returns:
        Total pod count
    """
    return len(_get_all_pods(ctx))


def _node_metrics(ctx: str) -> list[dict]:
    """Collect resource usage metrics for all nodes in the cluster.
    
    This function uses the metrics.k8s.io API to get CPU and memory usage
    for each node. It requires the metrics-server to be installed in the cluster.
    
    Args:
        ctx: Kubernetes context name
        
    Returns:
        List of dictionaries with node metrics information
        
    Note:
        CPU values are converted to cores and memory values to bytes
        using the quantity conversion functions.
    """
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
    """Find pods that have restarted in the last hour.
    
    This function checks container statuses to find pods with containers
    that have terminated and restarted within the last hour.
    
    Args:
        ctx: Kubernetes context name
        
    Returns:
        List of dictionaries with information about recently restarted pods
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
def collect(selected: tuple[str, ...]) -> dict:
    """Collect data from multiple clusters in parallel.
    
    This function is the main entry point for data collection. It uses
    ThreadPoolExecutor to collect data from multiple clusters in parallel,
    which significantly improves performance when monitoring multiple clusters.
    
    Args:
        selected: Tuple of Kubernetes context names to collect data from
        
    Returns:
        Dictionary containing aggregated data from all selected clusters:
        - total_pods: Total number of pods across all clusters
        - non_running_total: Total number of non-running pods
        - non_running_pods: List of non-running pods with details
        - node_metrics: List of node metrics from all clusters
        - recent_restarts: List of recently restarted pods
    """
    with ThreadPoolExecutor() as pool:
        # Collect data from all clusters in parallel
        non_running_lists = list(pool.map(_non_running_pods_list, selected))
        non_running = [len(nr_list) for nr_list in non_running_lists]
        total_pods = list(pool.map(_total_pods, selected))
        nodes = sum(pool.map(_node_metrics, selected), [])
        restarts = sum(pool.map(_recent_restarts, selected), [])

    # Aggregate and return the collected data
    return {
        "total_pods": sum(total_pods),
        "non_running_total": sum(non_running),
        "non_running_pods": sum(non_running_lists, []),
        "node_metrics": nodes,
        "recent_restarts": restarts,
    }
