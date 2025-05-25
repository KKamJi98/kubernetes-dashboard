"""Kubernetes API handler caching for each cluster.

이 모듈은 Kubernetes API 클라이언트를 생성하고 캐싱하는 기능을 제공합니다.
각 클러스터 컨텍스트별로 API 클라이언트를 캐싱하여 성능을 향상시킵니다.
"""

from functools import lru_cache

from kubernetes import client, config


@lru_cache(maxsize=16)
def api_for(context: str):
    """특정 컨텍스트에 대한 Kubernetes API 클라이언트를 반환합니다.

    LRU 캐시를 사용하여 동일한 컨텍스트에 대한 반복 호출을 최적화합니다.
    최대 16개의 다른 컨텍스트를 캐싱할 수 있습니다.

    Args:
        context (str): Kubernetes 컨텍스트 이름

    Returns:
        tuple: (CoreV1Api, CustomObjectsApi) 클라이언트 객체 튜플
    """
    config.load_kube_config(context=context)
    return client.CoreV1Api(), client.CustomObjectsApi()
