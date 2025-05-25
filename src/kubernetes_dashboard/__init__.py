"""Kubernetes Multi-Cluster Dashboard package.

This package provides a Streamlit-based dashboard for monitoring multiple
Kubernetes clusters simultaneously. It allows users to view pod status,
node resource usage, and pod restart information across multiple clusters.

Key modules:
- dashboard.py: Main Streamlit UI implementation
- collectors.py: Data collection from Kubernetes clusters
- quantity.py: Kubernetes resource quantity conversion utilities
- kube_client.py: Kubernetes API client with caching

The dashboard can be run directly with:
    python -m kubernetes_dashboard
    
Or through the main.py wrapper:
    python main.py
"""

__version__ = "0.1.0"
