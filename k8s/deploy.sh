#!/bin/bash

# Kubernetes Deployment Script for Iris Classifier
# Supports: standard, canary, and blue-green deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="iris-classifier"
DEPLOYMENT_TYPE="${1:-standard}"
IMAGE_TAG="${2:-latest}"
REGISTRY="${3:-localhost:5000}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_warning "docker is not installed (needed for building images)"
    fi
    
    log_success "Prerequisites check passed"
}

# Create namespace
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    kubectl apply -f k8s/namespace.yaml
    log_success "Namespace created"
}

# Build and push Docker image
build_image() {
    log_info "Building Docker image: $REGISTRY/iris-classifier:$IMAGE_TAG"
    docker build -t $REGISTRY/iris-classifier:$IMAGE_TAG .
    
    log_info "Pushing image to registry..."
    docker push $REGISTRY/iris-classifier:$IMAGE_TAG
    
    log_success "Image built and pushed"
}

# Deploy standard deployment
deploy_standard() {
    log_info "Deploying standard deployment..."
    
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Standard deployment completed"
}

# Deploy canary deployment
deploy_canary() {
    log_info "Deploying canary deployment..."
    
    # First deploy stable version
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    
    # Then deploy canary
    kubectl apply -f k8s/canary.yaml
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Canary deployment completed"
    log_info "Canary is receiving 10% of traffic"
}

# Deploy blue-green deployment
deploy_blue_green() {
    log_info "Deploying blue-green deployment..."
    
    # Deploy both blue and green
    kubectl apply -f k8s/blue-green.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Blue-green deployment completed"
    log_info "Blue deployment is active, green is standby"
}

# Wait for deployment
wait_for_deployment() {
    local deployment=$1
    local timeout=${2:-300}
    
    log_info "Waiting for deployment: $deployment (timeout: ${timeout}s)"
    
    kubectl rollout status deployment/$deployment \
        -n $NAMESPACE \
        --timeout=${timeout}s
    
    log_success "Deployment $deployment is ready"
}

# Check deployment status
check_status() {
    log_info "Checking deployment status..."
    
    echo ""
    echo "Deployments:"
    kubectl get deployments -n $NAMESPACE
    
    echo ""
    echo "Pods:"
    kubectl get pods -n $NAMESPACE
    
    echo ""
    echo "Services:"
    kubectl get services -n $NAMESPACE
    
    echo ""
    echo "Ingress:"
    kubectl get ingress -n $NAMESPACE
}

# Get deployment info
get_info() {
    log_info "Getting deployment information..."
    
    echo ""
    echo "API Endpoint:"
    kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[0].spec.rules[0].host}'
    echo ""
    
    echo ""
    echo "Pod IPs:"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo ""
    echo "Service IPs:"
    kubectl get services -n $NAMESPACE -o wide
}

# Scale deployment
scale_deployment() {
    local deployment=$1
    local replicas=$2
    
    log_info "Scaling $deployment to $replicas replicas..."
    
    kubectl scale deployment/$deployment \
        -n $NAMESPACE \
        --replicas=$replicas
    
    log_success "Deployment scaled"
}

# Rollback deployment
rollback_deployment() {
    local deployment=$1
    
    log_info "Rolling back deployment: $deployment"
    
    kubectl rollout undo deployment/$deployment -n $NAMESPACE
    
    log_success "Deployment rolled back"
}

# Main
main() {
    log_info "Starting Iris Classifier Kubernetes Deployment"
    log_info "Deployment Type: $DEPLOYMENT_TYPE"
    log_info "Image Tag: $IMAGE_TAG"
    log_info "Registry: $REGISTRY"
    
    check_prerequisites
    create_namespace
    
    case $DEPLOYMENT_TYPE in
        standard)
            deploy_standard
            wait_for_deployment "iris-classifier"
            ;;
        canary)
            deploy_canary
            wait_for_deployment "iris-classifier"
            wait_for_deployment "iris-classifier-canary"
            ;;
        blue-green)
            deploy_blue_green
            wait_for_deployment "iris-classifier-blue"
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            echo "Usage: $0 [standard|canary|blue-green] [image-tag] [registry]"
            exit 1
            ;;
    esac
    
    check_status
    get_info
    
    log_success "Deployment completed successfully!"
}

# Run main
main

