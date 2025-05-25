#!/usr/bin/env python3
"""
Kubernetes Multi-Cluster Dashboard - Main Execution Script

This script serves as the primary entry point for running the Kubernetes
multi-cluster dashboard application from the project's root directory.

It acts as a thin wrapper around the Streamlit CLI, configuring it to run
the dashboard.py module from the src/kubernetes_dashboard package.

Usage:
    python main.py

This approach provides a convenient way to start the dashboard without
having to specify the full path to the dashboard.py file or use the
module execution syntax.

Note:
    This script directly manipulates sys.argv to avoid Streamlit CLI warnings
    that would otherwise appear when using subprocess or other approaches.
"""
import os
import sys

import streamlit.web.cli as stcli

if __name__ == "__main__":
    # Configure Streamlit CLI arguments to run the dashboard
    # This approach prevents warning messages that would appear with other methods
    sys.argv = [
        "streamlit",
        "run",
        os.path.join(
            os.path.dirname(__file__), "src/kubernetes_dashboard/dashboard.py"
        ),
    ]
    # Execute Streamlit CLI and exit with its return code
    sys.exit(stcli.main())
