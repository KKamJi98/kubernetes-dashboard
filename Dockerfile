FROM python:3.13-slim

WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# kubectl 설치
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Poetry 설치
RUN pip install uv

# 의존성 파일 복사
COPY pyproject.toml ./
RUN uv pip install -r pyproject.toml --system

# 소스 코드 복사
COPY . .
RUN uv pip install . --system

# 포트 설정
EXPOSE 8501

# 실행 명령
CMD ["python", "main.py"]
