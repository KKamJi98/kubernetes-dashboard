# K8s Multi-Cluster Dashboard 요구사항

이 프로젝트는 Streamlit을 사용하여 구축된 오픈 소스 멀티 클러스터 Kubernetes 대시보드입니다.

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 프로젝트 구조

```
kubernetes-dashboard/
├─ pyproject.toml
├─ poetry.lock
├─ LICENSE
├─ README.md
├─ CONTRIBUTING.md
├─ project-requirements.md
├─ main.py
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ kubernetes/
│  └─ test/
│     ├─ pending-pod.yaml
│     └─ restarting-pod.yaml
└─ src/
   └─ kubernetes_dashboard/
      ├─ __init__.py
      ├─ __main__.py
      ├─ kube_client.py
      ├─ quantity.py
      ├─ collectors.py
      └─ dashboard.py
```

## 핵심 기능

1. **멀티 클러스터 모니터링**
   - 여러 Kubernetes 클러스터를 동시에 모니터링
   - 사이드바에서 클러스터 컨텍스트 선택 가능

2. **리소스 사용량 시각화**
   - 노드별 CPU 및 메모리 사용량 표시
   - CPU는 cores 단위(소수점 2자리)로 표시
   - 메모리는 GiB 단위(소수점 2자리)로 표시

3. **Pod 상태 모니터링**
   - Total Pods와 Unhealthy Pods 수 표시
   - Non-Running 상태의 Pod 목록 표시
   - 최근 1시간 내 재시작된 Pod 목록 표시

4. **네비게이션 구조**
   - **Overview 페이지**: 선택된 모든 클러스터의 요약 정보
   - **클러스터별 페이지**: 각 클러스터의 상세 정보

## 구현 요구사항

### 1. 대시보드 UI

#### Overview 페이지
- Total Pods / Unhealthy Pods 지표
- Non-Running Pods 목록
- Top-3 메모리 사용 노드 테이블 (인덱스 0부터 시작)
- Top-3 CPU 사용 노드 테이블 (인덱스 0부터 시작)
- 최근 1시간 내 재시작된 Pod 목록

#### 클러스터별 상세 페이지
- Total Pods / Unhealthy Pods 지표
- Non-Running Pods 목록
- 노드별 리소스 사용량 테이블 (메모리, CPU)
- 최근 1시간 내 재시작된 Pod 목록 (해당 클러스터만)

### 2. 데이터 수집

- Kubernetes API를 통한 실시간 데이터 수집
- 멀티 클러스터 병렬 데이터 수집 (ThreadPoolExecutor 사용)
- 메트릭 변환 (Kubernetes quantity → 표준 단위)

### 3. 리소스 단위 포맷

- CPU usage → **cores** 단위(소수점 2자리)로 표시
- Memory usage → **GiB** 단위(소수점 2자리)로 표시

## 테스트 환경

- Pending 상태 Pod 및 재시작되는 Pod를 생성하는 매니페스트 파일 제공
- `kubernetes/test/` 디렉토리에 테스트용 매니페스트 파일 포함

## 실행 방법

```bash
# 최상위 디렉토리에서 직접 실행
python main.py

# Poetry를 사용하여 실행
poetry run dashboard

# 또는 Streamlit으로 직접 실행
poetry run streamlit run src/kubernetes_dashboard/dashboard.py

# 모듈로 직접 실행
python -m kubernetes_dashboard
```

## 코드 품질 관리

1. **코드 포맷팅**
   - Black을 사용한 일관된 코드 스타일 적용
   - isort를 사용한 import 문 정렬
   - CI 파이프라인에서 코드 스타일 검사 자동화

2. **CI 파이프라인**
   - GitHub Actions를 통한 자동 테스트 및 코드 품질 검사
   - Black 및 isort 검사를 통과해야 빌드 성공

3. **Black과 isort 통합 설정**
   - pyproject.toml에 다음 설정을 추가하여 두 도구가 일관되게 작동하도록 함:
   ```toml
   [tool.black]
   line-length = 88
   target-version = ["py313"]
   include = '\.pyi?$'

   [tool.isort]
   profile = "black"
   line_length = 88
   multi_line_output = 3
   include_trailing_comma = true
   force_grid_wrap = 0
   use_parentheses = true
   ensure_newline_before_comments = true
   ```
   - `profile = "black"` 설정으로 isort가 black과 호환되는 스타일 사용
   - 동일한 line_length 값으로 일관된 라인 길이 유지

## 향후 개선 사항

1. **자동 새로고침 기능**
   - Streamlit 자동 새로고침을 통한 실시간 업데이트

2. **로그/이벤트 페이지 추가**
   - Pod 로그 및 클러스터 이벤트 조회 기능

3. **Docker 배포**
   - 컨테이너화된 대시보드 배포 지원

4. **코드 품질 자동화**
   - pre-commit 훅을 통한 코드 포맷팅 및 테스트 자동화