## Rules

- **커밋:** Conventional Commits 사양을 따르며, `googleapis/release-please-action@v4`에 맞춰 커밋 메시지를 영어로 작성합니다.
- **버전 관리:** 시맨틱 버전 관리(vX.X.X)를 사용합니다.
- **포맷팅:** 코드는 `black`과 `ruff`로 포맷팅합니다.
- **코드 품질:** `black`, `ruff`, `mypy`, `pytest`를 모두 통과한 상태에서만 GitHub에 커밋 및 푸시합니다.
- **문서 업데이트:** `CHANGELOG.md`는 항상 현재 형식에 맞춰 갱신하고, `README.md`는 현재 프로젝트와 변경사항을 기반으로 항상 최신화합니다.

## Requirement

- **패키지 관리자:** `uv`

# K8s Multi-Cluster Dashboard 요구사항

이 프로젝트는 Streamlit을 사용하여 구축된 오픈 소스 멀티 클러스터 Kubernetes 대시보드입니다.

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 프로젝트 구조

```
kubernetes-dashboard/
├─ pyproject.toml
├─ LICENSE
├─ README.md
├─ CONTRIBUTING.md
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
   - CPU 및 메모리 사용량을 퍼센트(%)로도 표시

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
- CPU 및 Memory 사용량 → **퍼센트(%)** 단위(소수점 2자리)로 표시

## 테스트 환경

- Pending 상태 Pod 및 재시작되는 Pod를 생성하는 매니페스트 파일 제공
- `kubernetes/test/` 디렉토리에 테스트용 매니페스트 파일 포함

## 실행 방법

```bash
# 최상위 디렉토리에서 직접 실행
python main.py

# uv를 사용하여 실행
uv run dashboard

# 또는 Streamlit으로 직접 실행
uv run streamlit run src/kubernetes_dashboard/dashboard.py

# 모듈로 직접 실행
python -m kubernetes_dashboard
```

# Important Notes

1. **코드 포맷팅**
   - Black을 사용한 일관된 코드 스타일 적용
   - isort를 사용한 import 문 정렬
   - CI 파이프라인에서 코드 스타일 검사 자동화

2. **CI 파이프라인**
   - GitHub Actions를 통한 자동 테스트 및 코드 품질 검사
   - Black, isort, pytest 검사를 통과해야 빌드 성공

3. **테스트 자동화**
   - pytest를 사용한 단위 테스트 작성
   - CI 파이프라인에서 테스트 자동 실행
   - 테스트, black, isort가 모두 통과해야 빌드 성공
   - `run_and_test.sh` 스크립트를 사용하여 헤드리스 모드에서 테스트 실행

4. **문서화**
   - README.md 파일에 프로젝트 개요 및 사용법 작성
   - 현재 파일 `GEMINI.md` 파일에 기능 요구사항 및 구현 사항 갱신
   - 코드 주석 및 docstring을 통한 함수 및 클래스 설명 추가
   - 변경 사항이 생길 때마다 `GEMINI.md` 파일의 History 섹션에 기록

5. **개발 환경**
   - uv를 사용한 의존성 관리
   - 가상 환경에서 개발 및 테스트 수행
   - Docker & Kubernetes를 사용한 배포 환경 구성

6. **커밋 컨벤션**
   - Conventional Commits 스타일을 따름 (ex: feat: add new feature, fix: bug fix, docs: update documentation)
   - 커밋은 영어로 짧고 간결하게 작성할 것

7. **코드 품질**
   - 가독성, 유지보수성, 확장성을 고려한 코드 작성
   - 공식 문서��� Best Practice를 따름
   - black, isort, pytest를 항상 통과할 것

8. **개발 규칙**
   - 현재 프로젝트 구조의 일관성을 유지하고 Best Practice를 따름
   - 기존 코드의 개선 사항은 (Amazon Q Recommend라는 표시 및 향후 개선 사항에 기록) (**필수!!**)
   - README.md 파일에 항상 최신 상태를 자세하게 반영

## Problem

- 현재 프로젝트에서 테스트 자동화 및 CI/CD 파이프라인 개선이 필요함
- Pod 리소스 사용량 모니터링 기능이 부족함
- 사용자 인증 및 권한 관리 기능이 없음

## Requirements

### 1. **테스트 자동화 개선**
- 헤드리스 모드에서 테스트를 실행하는 스크립트 추가
- 코드 포맷팅 검사 자동화

### 2. **Pod 리소스 사용량 모니터링 강화**
- Pod별 CPU 및 메모리 사용량 시각화 개선
- 리소스 사용량 기반 경고 설정 기능 추가

### 3. **사용자 인증 및 권한 관리**
- 대시보드 접근을 위한 인증 기능 추가
- 역할 기반 접근 제어(RBAC) 구현

## 향후 개선 사항

1. **성능 최적화**
   - 대규모 클러스터에서의 성능 개선
   - 데이터 캐싱 메커니즘 구현
   - 비동기 데이터 로딩 적용

2. **알림 시스템**
   - 이메일, Slack 등을 통한 알림 기능 추가
   - 사용자 정의 알림 규칙 설정 기능

3. **대시보드 커스터마이징**
   - 사용자별 대시보드 레이아웃 저장 기능
   - 커스텀 위젯 추가 기능

4. **다국어 지원**
   - 영어, 한국어 등 다양한 언어 지원
   - 지역화(localization) 프레임워크 적용

5. **클러스터 관리 기능 확장**
   - 리소스 생성 및 수정 기능 추가
   - 배치 작업 관리 기능
   - 네트워크 정책 시각화 및 관리

6. **보안 강화**
   - kubeconfig 암호화 저장 기능 개선
   - 접근 로그 및 감사 기능 추가

## History

This project uses `googleapis/release-please-action@v4` to automate release management.
The commit history is automatically managed and reflected in the CHANGELOG.md file.

- 2025-07-08: Switched from Poetry to uv for dependency management.
- 2025-06-04: Added `run_and_test.sh` script for automated test execution.
- 2025-06-04: Implemented kubeconfig file management via Kubernetes secrets.
- 2025-06-04: Added Pod log and cluster event viewing functionality.
- 2025-06-04: Implemented auto-refresh functionality.
- 2025-06-04: Configured Docker and Kubernetes deployment environments.
- 2025-05-30: Maintained current display units of cores and GiB.
- 2025-05-26: Added CPU Usage (%) and Memory Usage (%) columns to the node resource table.
- 2025-05-22: Displayed usage percentages with two decimal places (e.g., 45.67%).
- 2025-05-22: Displayed "N/A" if the metrics-server is not installed.
