# K8s Multi-Cluster Dashboard 요구사항

이 프로젝트는 Streamlit을 사용하여 구축된 오픈 소스 멀티 클러스터 Kubernetes 대시보드입니다.

---

## 프로젝트 구조

```md
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

---

## Rules

### 커밋 및 버전 관리

- Conventional Commits 사양을 따르며, `googleapis/release-please-action@v4`에 맞춰 커밋 메시지를 영어로 작성
- 시맨틱 버전 관리(vX.X.X) 사용

### 코드 품질 관리

- 코드는 `black`과 `ruff`로 포맷팅
- `ruff`는 0.13.3 버전으로 고정되어 있으며 pre-commit과 CI가 동일한 명령(`ruff check . --fix --exit-non-zero-on-fix`)을 실행합니다.
- `uv run ruff check . --fix --exit-non-zero-on-fix` 명령 실행 시 수정 사항이 발생하지 않을 때까지 반복하고, 두 번째 실행에서도 성공하는지 확인합니다.
- `black`, `ruff`, `mypy`, `pytest`를 모두 통과한 상태에서만 GitHub에 커밋 및 푸시

### 문서 관리

- `CHANGELOG.md`는 항상 현재 형식에 맞춰 갱신
- `README.md`는 현재 프로젝트와 변경사항을 기반으로 항상 최신화

---

## Requirements

### 패키지 관리

- 패키지 관리자: `uv`

### 대시보드 UI 구현

- Overview 페이지: Total Pods / Unhealthy Pods 지표, Non-Running Pods 목록, Top-3 메모리/CPU 사용 노드 테이블, 최근 1시간 내 재시작된 Pod 목록
- 클러스터별 상세 페이지: 클러스터별 Total Pods / Unhealthy Pods 지표, Non-Running Pods 목록, 노드별 리소스 사용량 테이블, 해당 클러스터의 최근 1시간 내 재시작된 Pod 목록

### 데이터 수집


- Kubernetes API를 통한 실시간 데이터 수집
- 멀티 클러스터 병렬 데이터 수집 (ThreadPoolExecutor 사용)
- 메트릭 변환 (Kubernetes quantity → 표준 단위)

### 리소스 단위 포맷

- CPU usage: cores 단위(소수점 2자리)로 표시
- Memory usage: GiB 단위(소수점 2자리)로 표시
- CPU 및 Memory 사용량: 퍼센트(%) 단위(소수점 2자리)로 표시

### 테스트 환경

- Pending 상태 Pod 및 재시작되는 Pod를 생성하는 매니페스트 파일 제공
- `kubernetes/test/` 디렉토리에 테스트용 매니페스트 파일 포함

### 추가 요구사항

- 테스트 자동화 개선: 헤드리스 모드에서 테스트를 실행하는 스크립트 추가, 코드 포맷팅 검사 자동화
- Pod 리소스 사용량 모니터링 강화: Pod별 CPU 및 메모리 사용량 시각화 개선, 리소스 사용량 기반 경고 설정 기능 추가
- 사용자 인증 및 권한 관리: 대시보드 접근을 위한 인증 기능 추가, 역할 기반 접근 제어(RBAC) 구현

---

## Core Functions

### 멀티 클러스터 모니터링

- 여러 Kubernetes 클러스터를 동시에 모니터링
- 사이드바에서 클러스터 컨텍스트 선택 가능

### 리소스 사용량 시각화

- 노드별 CPU 및 메모리 사용량 표시
- CPU는 cores 단위(소수점 2자리)로 표시
- 메모리는 GiB 단위(소수점 2자리)로 표시
- CPU 및 메모리 사용량을 퍼센트(%)로도 표시

### Pod 상태 모니터링

- Total Pods와 Unhealthy Pods 수 표시
- Non-Running 상태의 Pod 목록 표시
- 최근 1시간 내 재시작된 Pod 목록 표시

### 네비게이션 구조

- Overview 페이지: 선택된 모든 클러스터의 요약 정보
- 클러스터별 페이지: 각 클러스터의 상세 정보

---

## Future

### 성능 최적화

- 대규모 클러스터에서의 성능 개선
- 데이터 캐싱 메커니즘 구현
- 비동기 데이터 로딩 적용

### 알림 시스템

- 이메일, Slack 등을 통한 알림 기능 추가
- 사용자 정의 알림 규칙 설정 기능

### 대시보드 커스터마이징

- 사용자별 대시보드 레이아웃 저장 기능
- 커스텀 위젯 추가 기능

## Future improvements

---

### 다국어 지원

- 영어, 한국어 등 다양한 언어 지원
- 지역화(localization) 프레임워크 적용

### 클러스터 관리 기능 확장

- 리소스 생성 및 수정 기능 추가
- 배치 작업 관리 기능
- 네트워크 정책 시각화 및 관리

### 보안 강화

- kubeconfig 암호화 저장 기능 개선
- 접근 로그 및 감사 기능 추가
