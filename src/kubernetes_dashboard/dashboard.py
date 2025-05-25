"""Main dashboard application with overview + per-cluster pages."""

import pandas as pd
import streamlit as st
from kubernetes.config.kube_config import list_kube_config_contexts

from kubernetes_dashboard.collectors import collect, _non_running_pods, _total_pods
from kubernetes_dashboard.quantity import fmt_bytes_gib, fmt_cores


def main():
    """대시보드 메인 함수"""
    # ---------- Page setup ----------
    st.set_page_config("K8s Multi-Cluster Dashboard", layout="wide")

    # ---------- Sidebar: cluster multi-select ----------
    contexts, _ = list_kube_config_contexts()
    ctx_names = [c["name"] for c in contexts]
    selected = st.sidebar.multiselect(
        "Select Clusters", ctx_names, default=ctx_names[:1]
    )
    if not selected:
        st.stop()

    # ---------- Page navigation ----------
    page = st.sidebar.radio("🗂️ Pages", ["Overview"] + selected, index=0)

    # ---------- Collect data once for all pages ----------
    data = collect(tuple(selected))
    df_nodes = pd.DataFrame(data["node_metrics"])

    # ======================================================
    # ================  Overview  ==========================
    # ======================================================
    if page == "Overview":
        st.header("📊 Overview (Selected Clusters)")

        # Pod 상태 지표
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Pods", data["total_pods"])
        with col2:
            st.metric("Unhealthy Pods", data["non_running_total"])

        # Non-running pods list
        if data["non_running_pods"]:
            st.subheader("Non-Running Pods")
            st.dataframe(pd.DataFrame(data["non_running_pods"]))
        else:
            st.success("모든 Pod가 정상적으로 실행 중입니다.")

        # Format node metrics
        if not df_nodes.empty:
            df_nodes["mem (GiB)"] = df_nodes["mem"].apply(fmt_bytes_gib)
            df_nodes["cpu (cores)"] = df_nodes["cpu"].apply(fmt_cores)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top-3 Memory Nodes")
                # reset_index()를 추가하여 인덱스를 0부터 시작하도록 설정
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

        # Recent restarts (all clusters)
        if data["recent_restarts"]:
            st.subheader("Pods Restarted in Last Hour")
            st.dataframe(pd.DataFrame(data["recent_restarts"]))
        else:
            st.success("최근 1시간 내 재시작된 Pod가 없습니다.")

    # ======================================================
    # ===========  Per-Cluster detailed pages  =============
    # ======================================================
    else:
        cluster = page  # page value equals context name
        st.header(f"🔍 Cluster Detail — {cluster}")

        # ------- Pod 상태 지표 -------
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Pods", _total_pods(cluster))
        with col2:
            st.metric("Unhealthy Pods", _non_running_pods(cluster))

        # Non-running pods list for this cluster
        cluster_non_running_pods = [
            p for p in data["non_running_pods"] if p["cluster"] == cluster
        ]
        if cluster_non_running_pods:
            st.subheader("Non-Running Pods")
            st.dataframe(pd.DataFrame(cluster_non_running_pods))
        else:
            st.success("모든 Pod가 정상적으로 실행 중입니다.")

        # ------- Node table -------
        st.subheader("Node Resource Usage")
        node_df = df_nodes[df_nodes["cluster"] == cluster]
        if not df_nodes.empty:
            node_df = node_df.assign(
                memory=node_df["mem"].apply(fmt_bytes_gib),
                cpu=node_df["cpu"].apply(fmt_cores),
            )[["node", "memory", "cpu"]]
            st.dataframe(node_df, hide_index=True)
        else:
            st.info("노드 메트릭을 찾을 수 없습니다 (metrics-server 확인 필요).")

        # ------- Recent restarts -------
        restarts = [r for r in data["recent_restarts"] if r["cluster"] == cluster]
        if restarts:
            st.subheader("Pods Restarted in Last Hour")
            st.dataframe(pd.DataFrame(restarts))
        else:
            st.success("최근 1시간 내 재시작된 Pod가 없습니다.")


if __name__ == "__main__":
    main()
