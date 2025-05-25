"""Kubernetes API handler caching for each cluster context.

This module provides a cached API client factory for Kubernetes clusters.
It uses the kubernetes-client library to interact with Kubernetes API servers
and implements caching to avoid repeated client initialization for the same context.

The caching is particularly important for multi-cluster dashboards where
we need to switch between different cluster contexts frequently.
"""

from functools import lru_cache

from kubernetes import client, config


@lru_cache(maxsize=16)
def api_for(context: str):
    """Return Core & CustomObjects API clients for the given context name.
    
    This function creates and caches Kubernetes API clients for a specific cluster context.
    The LRU cache ensures we don't repeatedly initialize clients for the same context,
    which improves performance when switching between clusters in the dashboard.
    
    Args:
        context: The name of the Kubernetes context as defined in kubeconfig
        
    Returns:
        tuple: A tuple containing (CoreV1Api, CustomObjectsApi) clients
        
    Note:
        The function expects the kubeconfig file to be available at the default
        location (~/.kube/config) or as specified by KUBECONFIG environment variable.
    """
    config.load_kube_config(context=context)
    return client.CoreV1Api(), client.CustomObjectsApi()
