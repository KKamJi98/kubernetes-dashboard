# Black Formatting Fixes Required

The pipeline is failing due to black formatting checks. The following files need to be reformatted:

1. `/src/kubernetes_dashboard/__main__.py`
2. `/src/kubernetes_dashboard/kube_client.py`
3. `/tests/test_quantity.py`
4. `/src/kubernetes_dashboard/quantity.py`
5. `/src/kubernetes_dashboard/collectors.py`
6. `/src/kubernetes_dashboard/dashboard.py`

The error message from the pipeline:
```
would reformat /home/runner/work/kubernetes-dashboard/kubernetes-dashboard/src/kubernetes_dashboard/__main__.py
would reformat /home/runner/work/kubernetes-dashboard/kubernetes-dashboard/src/kubernetes_dashboard/kube_client.py
would reformat /home/runner/work/kubernetes-dashboard/kubernetes-dashboard/tests/test_quantity.py
would reformat /home/runner/work/kubernetes-dashboard/kubernetes-dashboard/src/kubernetes_dashboard/quantity.py
would reformat /home/runner/work/kubernetes-dashboard/kubernetes-dashboard/src/kubernetes_dashboard/collectors.py
would reformat /home/runner/work/kubernetes-dashboard/kubernetes-dashboard/src/kubernetes_dashboard/dashboard.py

Oh no! 💥 💔 💥
6 files would be reformatted, 2 files would be left unchanged.
```

## Fix Required

Run the black formatter on these files to comply with the style requirements:

```bash
black src/kubernetes_dashboard/__main__.py
black src/kubernetes_dashboard/kube_client.py
black tests/test_quantity.py
black src/kubernetes_dashboard/quantity.py
black src/kubernetes_dashboard/collectors.py
black src/kubernetes_dashboard/dashboard.py
```

Alternatively, format all Python files in the project:

```bash
black .
```

This will automatically reformat the code to follow black's style guide.