"""Main dashboard application with overview + per-cluster pages."""

import pandas as pd
import streamlit as st
from kubernetes.config.kube_config import list_kube_config_contexts

from kubernetes_dashboard.collectors import _non_running_pods, _total_pods, collect
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
            # N/A 값 처리
            df_nodes_filtered = df_nodes[~((df_nodes["cpu"] == "N/A") & (df_nodes["mem"] == "N/A"))]
            
            if not df_nodes_filtered.empty:
                # 숫자 형식의 데이터만 포함된 데이터프레임으로 필터링
                numeric_df = df_nodes_filtered[~((df_nodes_filtered["cpu"] == "N/A") | (df_nodes_filtered["mem"] == "N/A"))]
                
                if not numeric_df.empty:
                    numeric_df["mem (GiB)"] = numeric_df["mem"].apply(fmt_bytes_gib)
                    numeric_df["cpu (cores)"] = numeric_df["cpu"].apply(fmt_cores)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Top-3 Memory Nodes")
                        # reset_index()를 추가하여 인덱스를 0부터 시작하도록 설정
                        st.table(
                            numeric_df.nlargest(3, "mem")[["cluster", "node", "mem (GiB)"]]
                            .rename(columns={"mem (GiB)": "memory"})
                            .reset_index(drop=True)
                        )
                    with col2:
                        st.subheader("Top-3 CPU Nodes")
                        st.table(
                            numeric_df.nlargest(3, "cpu")[["cluster", "node", "cpu (cores)"]]
                            .rename(columns={"cpu (cores)": "cpu"})
                            .reset_index(drop=True)
                        )
                else:
                    st.info("metrics-server가 설치되지 않아 노드 리소스 사용량을 표시할 수 없습니다.")
            else:
                st.info("metrics-server가 설치되지 않아 노드 리소스 사용량을 표시할 수 없습니다.")
        else:
            st.info("노드 정보를 찾을 수 없습니다.")

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
        if not node_df.empty:
            # N/A 값 처리
            display_df = node_df.copy()
            
            # 문자열 "N/A"를 그대로 표시
            display_df["memory"] = [
                fmt_bytes_gib(row["mem"]) if row["mem"] != "N/A" else "N/A" 
                for _, row in display_df.iterrows()
            ]
            display_df["cpu"] = [
                fmt_cores(row["cpu"]) if row["cpu"] != "N/A" else "N/A" 
                for _, row in display_df.iterrows()
            ]
            
            st.dataframe(display_df[["node", "memory", "cpu"]], hide_index=True)
        else:
            st.info("노드 정보를 찾을 수 없습니다.")

        # ------- Recent restarts -------
        restarts = [r for r in data["recent_restarts"] if r["cluster"] == cluster]
        if restarts:
            st.subheader("Pods Restarted in Last Hour")
            st.dataframe(pd.DataFrame(restarts))
        else:
            st.success("최근 1시간 내 재시작된 Pod가 없습니다.")


if __name__ == "__main__":
    main()