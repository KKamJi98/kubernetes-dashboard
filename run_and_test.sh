#!/bin/bash

# Kubernetes Dashboard 테스트 스크립트
# Streamlit 앱을 헤드리스 모드로 시작하고, 테스트를 실행한 후 서버를 자동으로 종료합니다.

echo "Starting Kubernetes Dashboard in headless mode..."
# 백그라운드에서 Streamlit 앱 실행
poetry run streamlit run src/kubernetes_dashboard/dashboard.py --server.headless=true &
STREAMLIT_PID=$!

# Streamlit 서버가 시작될 때까지 대기
echo "Waiting for Streamlit server to start..."
sleep 5

echo "Running tests..."
# 테스트 실행
poetry run pytest -v

# 테스트 결과 저장
TEST_RESULT=$?

echo "Running code formatting checks..."
# 코드 포맷팅 검사
poetry run black --check .
BLACK_RESULT=$?

poetry run isort --check .
ISORT_RESULT=$?

# Streamlit 프로세스 종료
echo "Shutting down Streamlit server..."
kill $STREAMLIT_PID

# 결과 출력
echo "Test results: $TEST_RESULT"
echo "Black formatting check: $BLACK_RESULT"
echo "isort check: $ISORT_RESULT"

# 모든 검사가 통과했는지 확인
if [ $TEST_RESULT -eq 0 ] && [ $BLACK_RESULT -eq 0 ] && [ $ISORT_RESULT -eq 0 ]; then
    echo "All tests and checks passed successfully!"
    exit 0
else
    echo "Some tests or checks failed. Please check the output above."
    exit 1
fi
