# 테스트용 Kubernetes 매니페스트

이 디렉토리에는 K8s Multi-Cluster Dashboard를 테스트하기 위한 Kubernetes 매니페스트 파일이 포함되어 있습니다.

## 사용 방법

### Pending 상태 Pod 생성

```bash
kubectl apply -f pending-pod.yaml
```

이 Pod는 다음과 같은 이유로 Pending 상태가 됩니다:
- 매우 큰 리소스 요청 (CPU 50코어, 메모리 100GiB)
- 존재하지 않는 노드 셀렉터 조건

### 재시작되는 Pod 생성

```bash
kubectl apply -f restarting-pod.yaml
```

이 Pod는 다음과 같은 동작을 합니다:
- 10초 동안 실행된 후 종료 (exit 1)
- `restartPolicy: Always`로 인해 계속 재시작됨
- 대시보드에서 재시작 횟수 증가 확인 가능

## 테스트 정리

```bash
kubectl delete -f pending-pod.yaml
kubectl delete -f restarting-pod.yaml
```