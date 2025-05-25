"""Kubernetes API handler caching for each cluster."""

from functools import lru_cache
from kubernetes import client, config


@lru_cache(maxsize=16)
def api_for(context: str):
    """Return Core & CustomObjects API for the given context name."""
    config.load_kube_config(context=context)
    return client.CoreV1Api(), client.CustomObjectsApi()
