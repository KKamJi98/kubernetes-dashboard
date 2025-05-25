"""
Kubernetes Dashboard 모듈 실행 진입점

이 모듈은 Poetry 스크립트를 통해 대시보드를 실행할 때 사용되는 진입점입니다.
Streamlit CLI를 직접 호출하여 dashboard.py를 실행합니다.
"""

import os
import sys

import streamlit.web.cli as stcli


def main():
    """Poetry 스크립트 실행을 위한 진입점
    
    dashboard.py 파일의 경로를 찾아 Streamlit CLI를 통해 실행합니다.
    Poetry의 스크립트 엔트리 포인트로 사용됩니다.
    
    Returns:
        None: 프로그램 종료 코드는 sys.exit()을 통해 전달됩니다.
    """
    # Streamlit CLI를 직접 호출
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.py")
    sys.argv = ["streamlit", "run", dashboard_path]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
