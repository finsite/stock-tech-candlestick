name: Deploy to Kubernetes

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up kubectl
        run: |
          echo "$KUBECONFIG" > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml

      - name: Apply Kubernetes manifests
        run: kubectl apply -f k8s/
