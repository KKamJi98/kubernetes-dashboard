#!/bin/bash

# Kubernetes Dashboard 테스트 및 검증 스크립트

echo "Creating virtual environment and installing dependencies..."
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

echo "Running Ruff..."
ruff check . --fix --exit-non-zero-on-fix
RUFF_RESULT=$?

echo "Running Black..."
black . --check
BLACK_RESULT=$?

echo "Running MyPy..."
mypy .
MYPY_RESULT=$?

echo "Running tests..."
pytest
TEST_RESULT=$?

# 결과 출력
echo "Ruff check: $RUFF_RESULT"
echo "Black formatting check: $BLACK_RESULT"
echo "MyPy check: $MYPY_RESULT"
echo "Test results: $TEST_RESULT"

# 모든 검사가 통과했는지 확인
if [ $RUFF_RESULT -eq 0 ] && [ $BLACK_RESULT -eq 0 ] && [ $MYPY_RESULT -eq 0 ] && [ $TEST_RESULT -eq 0 ]; then
    echo "All tests and checks passed successfully!"
    exit 0
else
    echo "Some tests or checks failed. Please check the output above."
    exit 1
fi
