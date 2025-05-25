"""Main dashboard application with overview + per-cluster pages.

This module implements the Streamlit-based user interface for the Kubernetes
multi-cluster dashboard. It provides:

1. An overview page showing aggregated metrics from all selected clusters
2. Individual cluster pages showing detailed metrics for each cluster

The dashboard allows users to:
- Select multiple Kubernetes clusters to monitor
- View pod status (running, non-running)
- Monitor node resource usage (CPU, memory)
- Track pod restarts

The UI is built with Streamlit components like metrics, dataframes, and tables
to provide a clean and intuitive interface.
"""

import pandas as pd
import streamlit as st
from kubernetes.config.kube_config import list_kube_config_contexts

from kubernetes_dashboard.collectors import _non_running_pods, _total_pods, collect
from kubernetes_dashboard.quantity import fmt_bytes_gib, fmt_cores


def main():
    """Main dashboard application entry point.
    
    This function sets up the Streamlit UI and handles:
    1. Page configuration and layout
    2. Cluster selection via sidebar
    3. Navigation between overview and cluster-specific pages
    4. Data collection and visualization
    """
    # ---------- Page setup ----------
    st.set_page_config("K8s Multi-Cluster Dashboard", layout="wide")

    # ---------- Sidebar: cluster multi-select ----------
    # Get available Kubernetes contexts from kubeconfig
    contexts, _ = list_kube_config_contexts()
    ctx_names = [c["name"] for c in contexts]
    
    # Allow user to select multiple clusters to monitor
    selected = st.sidebar.multiselect(
        "Select Clusters", ctx_names, default=ctx_names[:1]
    )
    if not selected:
        st.stop()  # Stop execution if no clusters selected

    # ---------- Page navigation ----------
    # Radio buttons for navigation between overview and cluster-specific pages
    page = st.sidebar.radio("🗂️ Pages", ["Overview"] + selected, index=0)

    # ---------- Collect data once for all pages ----------
    # Collect data from all selected clusters in parallel
    data = collect(tuple(selected))
    df_nodes = pd.DataFrame(data["node_metrics"])

    # ======================================================
    # ================  Overview  ==========================
    # ======================================================
    if page == "Overview":
        st.header("📊 Overview (Selected Clusters)")

        # Pod status metrics - display total and unhealthy pod counts
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Pods", data["total_pods"])
        with col2:
            st.metric("Unhealthy Pods", data["non_running_total"])

        # Non-running pods list - show pods that need attention
        if data["non_running_pods"]:
            st.subheader("Non-Running Pods")
            st.dataframe(pd.DataFrame(data["non_running_pods"]))
        else:
            st.success("모든 Pod가 정상적으로 실행 중입니다.")

        # Format node metrics for display
        if not df_nodes.empty:
            # Convert raw values to human-readable formats
            df_nodes["mem (GiB)"] = df_nodes["mem"].apply(fmt_bytes_gib)
            df_nodes["cpu (cores)"] = df_nodes["cpu"].apply(fmt_cores)

            # Display top resource consumers in two columns
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top-3 Memory Nodes")
                # Reset index to start from 0 as required
                st.table(
                    df_nodes.nlargest(3, "mem")[["cluster", "node", "mem (GiB)"]]
                    .rename(columns={"mem (GiB)": "memory"})
                    .reset_index(drop=True)
                )
            with col2:
                st.subheader("Top-3 CPU Nodes")
                st.table(
                    df_nodes.nlargest(3, "cpu")[["cluster", "node", "cpu (cores)"]]
                    .rename(columns={"cpu (cores)": "cpu"})
                    .reset_index(drop=True)
                )

        # Recent pod restarts across all clusters
        if data["recent_restarts"]:
            st.subheader("Pods Restarted in Last Hour")
            st.dataframe(pd.DataFrame(data["recent_restarts"]))
        else:
            st.success("최근 1시간 내 재시작된 Pod가 없습니다.")

    # ======================================================
    # ===========  Per-Cluster detailed pages  =============
    # ======================================================
    else:
        # The page value equals the selected cluster context name
        cluster = page
        st.header(f"🔍 Cluster Detail — {cluster}")

        # ------- Pod status metrics for this cluster -------
        col1, col2 = st.columns(2)
        with col1:
            # Get cluster-specific pod count
            st.metric("Total Pods", _total_pods(cluster))
        with col2:
            # Get cluster-specific unhealthy pod count
            st.metric("Unhealthy Pods", _non_running_pods(cluster))

        # Non-running pods list for this specific cluster
        cluster_non_running_pods = [
            p for p in data["non_running_pods"] if p["cluster"] == cluster
        ]
        if cluster_non_running_pods:
            st.subheader("Non-Running Pods")
            st.dataframe(pd.DataFrame(cluster_non_running_pods))
        else:
            st.success("모든 Pod가 정상적으로 실행 중입니다.")

        # ------- Node resource usage table -------
        st.subheader("Node Resource Usage")
        # Filter node metrics for this specific cluster
        node_df = df_nodes[df_nodes["cluster"] == cluster]
        if not df_nodes.empty:
            # Format metrics for display
            node_df = node_df.assign(
                memory=node_df["mem"].apply(fmt_bytes_gib),
                cpu=node_df["cpu"].apply(fmt_cores),
            )[["node", "memory", "cpu"]]
            st.dataframe(node_df, hide_index=True)
        else:
            st.info("노드 메트릭을 찾을 수 없습니다 (metrics-server 확인 필요).")

        # ------- Recent pod restarts for this cluster -------
        # Filter restart data for this specific cluster
        restarts = [r for r in data["recent_restarts"] if r["cluster"] == cluster]
        if restarts:
            st.subheader("Pods Restarted in Last Hour")
            st.dataframe(pd.DataFrame(restarts))
        else:
            st.success("최근 1시간 내 재시작된 Pod가 없습니다.")


if __name__ == "__main__":
    main()
