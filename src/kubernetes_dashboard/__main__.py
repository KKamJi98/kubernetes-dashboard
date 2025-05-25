"""
Kubernetes Dashboard module execution entry point.

This module allows the dashboard to be run directly as a Python module:
    python -m kubernetes_dashboard

It configures the Streamlit CLI to run the dashboard.py file, which
contains the main dashboard application.

This approach is useful for:
1. Running the dashboard from the installed package
2. Integration with Poetry scripts
3. Providing a clean entry point for module execution
"""

import os
import sys

import streamlit.web.cli as stcli


def main():
    """Entry point for Poetry script execution and module invocation.
    
    This function:
    1. Configures Streamlit CLI arguments to run the dashboard
    2. Locates the dashboard.py file relative to this module
    3. Executes the Streamlit CLI with the appropriate arguments
    
    Returns:
        None: The function exits the process with Streamlit's exit code
    """
    # Find the dashboard.py file in the same directory as this module
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.py")
    
    # Configure Streamlit CLI arguments
    sys.argv = ["streamlit", "run", dashboard_path]
    
    # Execute Streamlit CLI and exit with its return code
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
