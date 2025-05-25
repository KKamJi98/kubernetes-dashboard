# 코드 전체에 대한 주석과 설명 추가

## 관련 이슈
- 코드 전체에 대한 주석과 설명 추가 (#1)

## 변경 내용
이 PR은 프로젝트의 모든 Python 파일에 상세한 주석과 설명을 추가하여 코드의 가독성과 유지보수성을 향상시킵니다.

### 추가된 문서화 내용
- 모든 모듈에 상세한 모듈 수준 docstring 추가
- 모든 함수에 매개변수, 반환값, 예외 정보를 포함한 docstring 추가
- 복잡한 로직에 대한 인라인 주석 추가
- 코드 흐름 및 아키텍처 설명 추가

### 변경된 파일
- `src/kubernetes_dashboard/__init__.py`
- `src/kubernetes_dashboard/__main__.py`
- `src/kubernetes_dashboard/collectors.py`
- `src/kubernetes_dashboard/dashboard.py`
- `src/kubernetes_dashboard/kube_client.py`
- `src/kubernetes_dashboard/quantity.py`
- `main.py`

## 테스트 방법
기능 변경이 없으므로 기존 테스트로 충분합니다.

## 체크리스트
- [x] PEP 257 docstring 규칙 준수
- [x] 함수의 목적, 매개변수, 반환값 명시
- [x] 복잡한 알고리즘이나 로직에 대한 설명 추가
- [x] 코드 예제 포함 (필요한 경우)

## 스크린샷
해당 없음 (문서화 작업만 수행)

## 기타 참고사항
이 PR은 코드 기능을 변경하지 않고 문서화만 개선합니다.
