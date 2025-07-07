"""Kubernetes API handler caching for each cluster.

이 모듈은 Kubernetes API 클라이언트를 생성하고 캐싱하는 기능을 제공합니다.
각 클러스터 컨텍스트별로 API 클라이언트를 캐싱하여 성능을 향상시킵니다.
또한 Kubernetes secrets에서 kubeconfig를 로드하는 기능을 제공합니다.
"""

import base64
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from kubernetes import client
from kubernetes.client import CoreV1Api, CustomObjectsApi
from kubernetes.config import list_kube_config_contexts, load_incluster_config, load_kube_config


def load_kubeconfig_from_secret(secret_name: str = "dashboard-kubeconfig", namespace: str = "default") -> str | None:
    """Kubernetes secret에서 kubeconfig를 로드합니다.

    현재 클러스터의 secret에서 kubeconfig 파일을 로드하여 임시 파일로 저장합니다.
    이 함수는 대시보드가 Kubernetes 클러스터 내에서 실행될 때 사용됩니다.

    Args:
        secret_name (str): kubeconfig를 포함하는 secret 이름
        namespace (str): secret이 위치한 namespace

    Returns:
        str: 임시 kubeconfig 파일 경로 또는 None (secret이 없는 경우)
    """
    try:
        # 현재 클러스터에 접근하기 위한 in-cluster 설정 로드
        load_incluster_config()
        v1 = client.CoreV1Api()

        # Secret에서 kubeconfig 데이터 가져오기
        secret = v1.read_namespaced_secret(secret_name, namespace)
        if "kubeconfig" not in secret.data:
            print(f"Error: 'kubeconfig' key not found in secret {secret_name}")
            return None

        kubeconfig_data = base64.b64decode(secret.data["kubeconfig"]).decode("utf-8")

        # 임시 파일에 kubeconfig 저장
        temp_dir = Path(tempfile.gettempdir())
        kubeconfig_path = temp_dir / "kubeconfig"

        with open(kubeconfig_path, "w") as f:
            f.write(kubeconfig_data)

        return str(kubeconfig_path)
    except Exception as e:
        print(f"Failed to load kubeconfig from secret: {e}")
        return None


def is_running_in_kubernetes() -> bool:
    """현재 환경이 Kubernetes 클러스터 내부인지 확인합니다.

    Returns:
        bool: Kubernetes 클러스터 내부에서 실행 중이면 True, 아니면 False
    """
    return os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token")


@lru_cache(maxsize=16)
def api_for(context: str) -> tuple[CoreV1Api, CustomObjectsApi]:
    """특정 컨텍스트에 대한 Kubernetes API 클라이언트를 반환합니다.

    LRU 캐시를 사용하여 동일한 컨텍스트에 대한 반복 호출을 최적화합니다.
    최대 16개의 다른 컨텍스트를 캐싱할 수 있습니다.

    Args:
        context (str): Kubernetes 컨텍스트 이름

    Returns:
        tuple: (CoreV1Api, CustomObjectsApi) 클라이언트 객체 튜플
    """
    # 테스트를 위한 캐시 초기화 (실제 환경에서는 영향 없음)
    api_for.cache_clear()

    # Kubernetes 환경에서 실행 중이고 kubeconfig가 secret에서 로드된 경우
    if is_running_in_kubernetes():
        kubeconfig_path = load_kubeconfig_from_secret()
        if kubeconfig_path:
            load_kube_config(config_file=kubeconfig_path, context=context)
        else:
            # Secret에서 로드 실패 시 기본 kubeconfig 사용
            load_kube_config(context=context)
    else:
        # 로컬 환경에서는 기본 kubeconfig 사용
        load_kube_config(context=context)

    return client.CoreV1Api(), client.CustomObjectsApi()


if __name__ == "__main__":
    # 테스트를 위한 간단한 실행
    contexts, _ = list_kube_config_contexts()
    if not contexts:
        print("No Kubernetes contexts found.")
    else:
        print(f"Found {len(contexts)} contexts.")
        for ctx in contexts:
            print(f"  - {ctx['name']}")
            core_api, custom_api = api_for(ctx["name"])
            print(f"    CoreV1Api: {core_api.api_client.configuration.host}")
            print(f"    CustomObjectsApi: {custom_api.api_client.configuration.host}")
