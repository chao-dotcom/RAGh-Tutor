#!/bin/bash

set -e

echo "Deploying RAG System to Kubernetes..."

# Build and push Docker image
echo "Building Docker image..."
docker build -t your-registry/rag-api:latest -f docker/Dockerfile .

echo "Pushing to registry..."
docker push your-registry/rag-api:latest

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Wait for deployment
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/rag-api -n rag-system

echo "Deployment complete!"
echo "Check status with: kubectl get pods -n rag-system"

