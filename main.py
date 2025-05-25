#!/usr/bin/env python3
"""
Kubernetes Multi-Cluster Dashboard - 메인 실행 파일

이 파일은 최상위 디렉토리에서 대시보드를 실행하기 위한 thin wrapper입니다.
사용자가 프로젝트 루트에서 직접 실행할 수 있도록 편의성을 제공합니다.
"""
import os
import sys

import streamlit.web.cli as stcli

if __name__ == "__main__":
    # Streamlit CLI를 직접 호출하여 경고 메시지 방지
    sys.argv = [
        "streamlit",
        "run",
        os.path.join(
            os.path.dirname(__file__), "src/kubernetes_dashboard/dashboard.py"
        ),
    ]
    sys.exit(stcli.main())
