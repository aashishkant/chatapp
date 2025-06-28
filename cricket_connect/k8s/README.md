# Kubernetes Manifests and Helm Charts

This directory will contain Kubernetes deployment manifests and/or Helm charts for deploying Cricket Connect to a Kubernetes cluster.

## Contents

- `deployments/`: Kubernetes YAML files for Deployments, Services, ConfigMaps, Secrets, etc.
- `charts/`: Helm chart(s) for easier package management and deployment on Kubernetes.

## Prerequisites

- Kubernetes cluster (e.g., Minikube, Kind, GKE, EKS, AKS)
- `kubectl` command-line tool configured to interact with your cluster
- Helm (if using Helm charts)

## Usage

### Using kubectl (Direct Manifests)

```bash
# Apply all manifests in a directory
kubectl apply -f deployments/

# Delete resources
kubectl delete -f deployments/
```

### Using Helm

```bash
# Install a chart (assuming a chart named 'cricket-connect' exists in 'charts/')
helm install cricket-connect ./charts/cricket-connect

# Upgrade a release
helm upgrade cricket-connect ./charts/cricket-connect

# Uninstall a release
helm uninstall cricket-connect
```

**Note:** Specific instructions will be added as manifests and charts are developed.
