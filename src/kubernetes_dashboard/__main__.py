"""
Kubernetes Dashboard 모듈 실행 진입점
"""
import streamlit.web.cli as stcli
import sys
import os

def main():
    """Poetry 스크립트 실행을 위한 진입점"""
    # Streamlit CLI를 직접 호출
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.py")
    sys.argv = ["streamlit", "run", dashboard_path]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()