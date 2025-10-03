"""Main dashboard application with overview + per-cluster pages.

이 모듈은 Streamlit을 사용하여 Kubernetes 멀티 클러스터 대시보드의
UI 및 데이터 시각화를 구현합니다. 대시보드는 여러 클러스터의 개요 페이지와
각 클러스터별 상세 페이지로 구성됩니다.

주요 기능:
- 여러 Kubernetes 클러스터 동시 모니터링
- Pod 상태 및 개수 표시
- 노드 리소스 사용량 시각화
- 최근 재시작된 Pod 추적
- Pod 로그 및 클러스터 이벤트 조회
- 자동 새로고침 기능
"""

import pandas as pd
import streamlit as st
from kubernetes.config.kube_config import list_kube_config_contexts

from kubernetes_dashboard.collectors import (
    _get_cluster_events,
    _get_pod_logs,
    _non_running_pods,
    _total_pods,
    collect,
)
from kubernetes_dashboard.kube_client import api_for
from kubernetes_dashboard.quantity import fmt_bytes_gib, fmt_cores, fmt_percent


def main() -> None:
    """대시보드 메인 함수

    Streamlit 애플리케이션의 진입점으로, 다음 기능을 수행합니다:
    1. 페이지 설정 및 레이아웃 구성
    2. 사이드바에서 클러스터 선택 UI 제공
    3. 페이지 네비게이션 (개요, 클러스터별 상세 페이지, 로그/이벤트 페이지)
    4. 선택된 클러스터에서 데이터 수집 및 시각화
    5. 자동 새로고침 설정
    """
    # ---------- Page setup ----------
    st.set_page_config("K8s Multi-Cluster Dashboard", layout="wide")

    # ---------- Sidebar: cluster multi-select ----------
    contexts, _ = list_kube_config_contexts()
    ctx_names = [c["name"] for c in contexts]
    selected = st.sidebar.multiselect("Select Clusters", ctx_names, default=ctx_names[:1])
    if not selected:
        st.stop()

    # ---------- 자동 새로고침 설정 ----------
    refresh_interval = st.sidebar.slider(
        "자동 새로고침 간격 (초)",
        min_value=0,
        max_value=300,
        value=0,
        step=30,
        help="0으로 설정하면 자동 새로고침이 비활성화됩니다.",
    )

    if refresh_interval > 0:
        st.sidebar.info(f"{refresh_interval}초마다 자동으로 새로고침됩니다.")
        st.sidebar.button("수동 새로고침")
        st.empty()  # 새로고침을 위한 빈 요소

        # 자동 새로고침 스크립트 추가
        st.markdown(
            f"""
            <script>
                var refreshInterval = {refresh_interval * 1000};
                setInterval(function() {{
                    window.location.reload();
                }}, refreshInterval);
            </script>
            """,
            unsafe_allow_html=True,
        )

    # ---------- Page navigation ----------
    pages = ["Overview", *selected, "Logs & Events"]
    page = st.sidebar.radio("🗂️ Pages", pages, index=0)

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
                numeric_df = df_nodes_filtered[
                    ~((df_nodes_filtered["cpu"] == "N/A") | (df_nodes_filtered["mem"] == "N/A"))
                ].copy()

                if not numeric_df.empty:
                    # 메모리와 CPU 값을 사람이 읽기 쉬운 형식으로 변환
                    numeric_df["mem (GiB)"] = numeric_df["mem"].apply(fmt_bytes_gib)
                    numeric_df["cpu (cores)"] = numeric_df["cpu"].apply(fmt_cores)
                    numeric_df["cpu %"] = numeric_df["cpu_percent"].apply(fmt_percent)
                    numeric_df["mem %"] = numeric_df["mem_percent"].apply(fmt_percent)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Top-3 Memory Nodes")
                        # reset_index()를 추가하여 인덱스를 0부터 시작하도록 설정
                        st.table(
                            numeric_df.nlargest(3, "mem")[["cluster", "node", "mem (GiB)", "mem %"]]
                            .rename(columns={"mem (GiB)": "memory"})
                            .reset_index(drop=True)
                        )
                    with col2:
                        st.subheader("Top-3 CPU Nodes")
                        st.table(
                            numeric_df.nlargest(3, "cpu")[["cluster", "node", "cpu (cores)", "cpu %"]]
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

        # 최근 이벤트 표시
        if data["events"]:
            st.subheader("Recent Events")
            events_df = pd.DataFrame(data["events"][:10])  # 최근 10개 이벤트만 표시
            st.dataframe(events_df[["cluster", "type", "reason", "object", "message", "time"]])
        else:
            st.info("최근 이벤트가 없습니다.")

    # ======================================================
    # ===========  Per-Cluster detailed pages  =============
    # ======================================================
    elif page in selected:
        # 클러스터별 상세 페이지 표시
        cluster = page  # page value equals context name
        st.header(f"🔍 Cluster Detail — {cluster}")

        # ------- Pod 상태 지표 -------
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Pods", _total_pods(cluster))
        with col2:
            st.metric("Unhealthy Pods", _non_running_pods(cluster))

        # Non-running pods list for this cluster
        cluster_non_running_pods = [p for p in data["non_running_pods"] if p["cluster"] == cluster]
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
                fmt_bytes_gib(row["mem"]) if row["mem"] != "N/A" else "N/A" for _, row in display_df.iterrows()
            ]
            display_df["cpu"] = [
                fmt_cores(row["cpu"]) if row["cpu"] != "N/A" else "N/A" for _, row in display_df.iterrows()
            ]
            display_df["cpu %"] = [
                (fmt_percent(row["cpu_percent"]) if row["cpu_percent"] != "N/A" else "N/A")
                for _, row in display_df.iterrows()
            ]
            display_df["memory %"] = [
                (fmt_percent(row["mem_percent"]) if row["mem_percent"] != "N/A" else "N/A")
                for _, row in display_df.iterrows()
            ]

            st.dataframe(
                display_df[["node", "memory", "memory %", "cpu", "cpu %"]],
                hide_index=True,
            )
        else:
            st.info("노드 정보를 찾을 수 없습니다.")

        # ------- Recent restarts -------
        restarts = [r for r in data["recent_restarts"] if r["cluster"] == cluster]
        if restarts:
            st.subheader("Pods Restarted in Last Hour")
            st.dataframe(pd.DataFrame(restarts))
        else:
            st.success("최근 1시간 내 재시작된 Pod가 없습니다.")

    # ======================================================
    # ================  Logs & Events  ====================
    # ======================================================
    elif page == "Logs & Events":
        st.header("📜 Logs & Events")

        # 탭 생성
        tab1, tab2 = st.tabs(["Pod Logs", "Cluster Events"])

        # Pod 로그 탭
        with tab1:
            st.subheader("Pod Logs")

            # 클러스터 선택
            cluster = st.selectbox("Select Cluster", selected)
            if not cluster:
                st.stop()

            # 네임스페이스 목록 가져오기
            core, _ = api_for(str(cluster))
            namespaces = [ns.metadata.name for ns in core.list_namespace().items]
            namespace = st.selectbox("Select Namespace", namespaces)
            if not namespace:
                st.stop()

            # 선택한 네임스페이스의 Pod 목록 가져오기
            pods = [pod.metadata.name for pod in core.list_namespaced_pod(namespace).items]
            if not pods:
                st.info(f"No pods found in namespace {namespace}")
            else:
                pod_name = st.selectbox("Select Pod", pods)
                if not pod_name:
                    st.stop()

                # 선택한 Pod의 컨테이너 목록 가져오기
                pod = core.read_namespaced_pod(pod_name, namespace)
                containers = [container.name for container in pod.spec.containers]
                container = st.selectbox("Select Container", containers)
                if not container:
                    st.stop()

                # 로그 라인 수 선택
                tail_lines = st.slider("Log Lines", min_value=10, max_value=500, value=100, step=10)

                # 로그 가져오기
                logs = _get_pod_logs(
                    str(cluster),
                    str(pod_name),
                    str(namespace),
                    str(container),
                    tail_lines,
                )

                # 로그 표시
                st.text_area("Pod Logs", logs, height=400)

        # 클러스터 이벤트 탭
        with tab2:
            st.subheader("Cluster Events")

            # 클러스터 및 네임스페이스 선택
            col1, col2 = st.columns(2)
            with col1:
                event_cluster = st.selectbox("Select Cluster for Events", selected, key="event_cluster")
                if not event_cluster:
                    st.stop()

            with col2:
                event_namespaces = ["All Namespaces"] + [
                    ns.metadata.name for ns in api_for(str(event_cluster))[0].list_namespace().items
                ]
                event_namespace = st.selectbox("Select Namespace for Events", event_namespaces)
                if not event_namespace:
                    st.stop()

            # 이벤트 수 선택
            event_limit = st.slider("Number of Events", min_value=10, max_value=500, value=100, step=10)

            # 이벤트 가져오기
            namespace_arg = None if event_namespace == "All Namespaces" else str(event_namespace)
            events = _get_cluster_events(str(event_cluster), namespace=namespace_arg, limit=event_limit)

            # 이벤트 표시
            if events:
                events_df = pd.DataFrame(events)
                st.dataframe(
                    events_df[["type", "reason", "object", "message", "time"]],
                    height=400,
                )
            else:
                st.info("No events found")


if __name__ == "__main__":
    main()
