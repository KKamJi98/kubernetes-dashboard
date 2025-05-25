# Kubernetes Test Manifests

This directory contains Kubernetes manifest files for testing the K8s Multi-Cluster Dashboard functionality. These manifests create pods in specific states to verify that the dashboard correctly detects and displays various pod conditions.

## Test Manifests Overview

The test manifests are designed to create pods that exhibit specific behaviors:

1. **pending-pod.yaml**: Creates a pod that remains in the Pending state
2. **restarting-pod.yaml**: Creates a pod that continuously crashes and restarts

## Usage Instructions

### Creating a Pending Pod

```bash
kubectl apply -f pending-pod.yaml
```

This manifest creates a pod that will remain in the Pending state due to:
- Extremely high resource requests (50 CPU cores, 100GiB memory) that cannot be satisfied by any node
- A node selector that specifies a non-existent label, preventing scheduling

The dashboard should detect this pod as "Non-Running" and display it in the appropriate sections.

### Creating a Restarting Pod

```bash
kubectl apply -f restarting-pod.yaml
```

This manifest creates a pod with the following behavior:
- The container runs for 10 seconds and then exits with an error code (exit 1)
- The `restartPolicy: Always` setting causes Kubernetes to continuously restart the container
- Each restart increments the restart counter, which should be visible in the dashboard

The dashboard should detect these restarts and display the pod in the "Pods Restarted in Last Hour" section.

## Testing Procedure

1. Apply one or both manifests to your Kubernetes cluster
2. Open the dashboard and verify that it correctly shows:
   - The pending pod in the "Non-Running Pods" section
   - The restarting pod in the "Pods Restarted in Last Hour" section
3. Check that the pod details (namespace, node, phase, reason, restart count) are displayed correctly

## Cleaning Up

When you're done testing, remove the test pods with:

```bash
kubectl delete -f pending-pod.yaml
kubectl delete -f restarting-pod.yaml
```

Or remove all test pods at once:

```bash
kubectl delete pods -l app=k8sdash-test
```