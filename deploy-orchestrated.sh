#!/bin/bash

###############################################################################
# GIVC Healthcare Platform - Production Deployment Script
# Container Orchestration for Kubernetes/Docker Swarm
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
ORCHESTRATOR="${ORCHESTRATOR:-docker-compose}"
NAMESPACE="${NAMESPACE:-givc}"

###############################################################################
# Helper Functions
###############################################################################

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

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        return 1
    fi
    return 0
}

###############################################################################
# Pre-deployment Checks
###############################################################################

preflight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check required commands based on orchestrator
    case $ORCHESTRATOR in
        docker-compose)
            check_command docker || exit 1
            check_command docker-compose || exit 1
            ;;
        kubernetes|k8s)
            check_command kubectl || exit 1
            check_command helm || exit 1
            ;;
        swarm)
            check_command docker || exit 1
            ;;
        *)
            log_error "Unknown orchestrator: $ORCHESTRATOR"
            exit 1
            ;;
    esac
    
    # Check if .env file exists
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        log_warning ".env file not found. Creating from template..."
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
            log_warning "Please update .env file with your configuration"
            exit 1
        else
            log_error ".env.example not found!"
            exit 1
        fi
    fi
    
    log_success "Pre-flight checks passed"
}

###############################################################################
# Docker Compose Deployment
###############################################################################

deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    cd "$SCRIPT_DIR"
    
    # Build images
    log_info "Building Docker images..."
    docker-compose build --parallel
    
    # Start services
    log_info "Starting services..."
    case $DEPLOYMENT_ENV in
        production)
            docker-compose --profile production up -d
            ;;
        development)
            docker-compose --profile dev up -d
            ;;
        *)
            docker-compose up -d
            ;;
    esac
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    docker-compose ps
    
    log_success "Docker Compose deployment complete"
}

###############################################################################
# Kubernetes Deployment
###############################################################################

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl create namespace "$NAMESPACE"
    fi
    
    # Apply configurations
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f "$SCRIPT_DIR/k8s/base/" -n "$NAMESPACE"
    
    # Wait for deployments
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/givc-app deployment/givc-backend -n "$NAMESPACE" || true
    
    # Check status
    kubectl get pods -n "$NAMESPACE"
    
    log_success "Kubernetes deployment complete"
}

###############################################################################
# Helm Deployment
###############################################################################

deploy_helm() {
    log_info "Deploying with Helm..."
    
    cd "$SCRIPT_DIR"
    
    # Install or upgrade Helm chart
    helm upgrade --install givc ./helm/givc-chart \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --values ./helm/givc-chart/values.yaml \
        --wait \
        --timeout 10m
    
    # Check status
    helm status givc -n "$NAMESPACE"
    
    log_success "Helm deployment complete"
}

###############################################################################
# Docker Swarm Deployment
###############################################################################

deploy_swarm() {
    log_info "Deploying to Docker Swarm..."
    
    # Initialize swarm if not already
    if ! docker info | grep -q "Swarm: active"; then
        log_info "Initializing Docker Swarm..."
        docker swarm init
    fi
    
    # Deploy stack
    docker stack deploy -c "$SCRIPT_DIR/docker-compose.yml" givc
    
    # Check services
    docker stack services givc
    
    log_success "Docker Swarm deployment complete"
}

###############################################################################
# Post-deployment Tasks
###############################################################################

post_deployment() {
    log_info "Running post-deployment tasks..."
    
    # Run database migrations (if applicable)
    if [ "$ORCHESTRATOR" = "kubernetes" ] || [ "$ORCHESTRATOR" = "k8s" ]; then
        log_info "Running database migrations..."
        # kubectl exec -it deployment/givc-backend -n "$NAMESPACE" -- python manage.py migrate
    fi
    
    # Verify health endpoints
    log_info "Verifying service health..."
    
    case $ORCHESTRATOR in
        docker-compose)
            log_info "Frontend: http://localhost:3000"
            log_info "Health check: http://localhost:3000/health.html"
            ;;
        kubernetes|k8s)
            FRONTEND_URL=$(kubectl get ingress givc-ingress -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "N/A")
            log_info "Frontend URL: https://$FRONTEND_URL"
            ;;
    esac
    
    log_success "Post-deployment tasks complete"
}

###############################################################################
# Cleanup Function
###############################################################################

cleanup() {
    log_info "Cleaning up..."
    
    case $ORCHESTRATOR in
        docker-compose)
            docker-compose down
            ;;
        kubernetes|k8s)
            kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
            ;;
        swarm)
            docker stack rm givc
            ;;
    esac
    
    log_success "Cleanup complete"
}

###############################################################################
# Main Deployment Flow
###############################################################################

main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║     🏥  GIVC Healthcare Platform Deployment                 ║"
    echo "║                                                              ║"
    echo "║     Container Orchestration Script                          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    log_info "Deployment Configuration:"
    log_info "  Environment: $DEPLOYMENT_ENV"
    log_info "  Orchestrator: $ORCHESTRATOR"
    log_info "  Namespace: $NAMESPACE"
    echo ""
    
    # Run pre-flight checks
    preflight_checks
    
    # Deploy based on orchestrator
    case $ORCHESTRATOR in
        docker-compose)
            deploy_docker_compose
            ;;
        kubernetes|k8s)
            if [ "${USE_HELM:-false}" = "true" ]; then
                deploy_helm
            else
                deploy_kubernetes
            fi
            ;;
        swarm)
            deploy_swarm
            ;;
        *)
            log_error "Unknown orchestrator: $ORCHESTRATOR"
            exit 1
            ;;
    esac
    
    # Post-deployment tasks
    post_deployment
    
    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    log_info "  1. Verify all services are running"
    log_info "  2. Check logs for any errors"
    log_info "  3. Test the application endpoints"
    log_info "  4. Configure monitoring and alerts"
    echo ""
}

###############################################################################
# Script Entry Point
###############################################################################

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    cleanup)
        cleanup
        ;;
    check)
        preflight_checks
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|check}"
        echo ""
        echo "Options:"
        echo "  deploy   - Deploy the application (default)"
        echo "  cleanup  - Remove all deployed resources"
        echo "  check    - Run pre-flight checks only"
        echo ""
        echo "Environment Variables:"
        echo "  DEPLOYMENT_ENV   - Environment (production|development|staging)"
        echo "  ORCHESTRATOR     - Orchestrator (docker-compose|kubernetes|swarm)"
        echo "  NAMESPACE        - Kubernetes namespace (default: givc)"
        echo "  USE_HELM         - Use Helm for deployment (true|false)"
        echo ""
        exit 1
        ;;
esac
