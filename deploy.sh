#!/bin/bash

# Multi-Agent Marketing System - Deployment Script
# This script handles the complete deployment of the system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "All prerequisites are met."
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        if [ -f env.template ]; then
            print_status "Creating .env file from template..."
            cp env.template .env
            print_warning "Please update the .env file with your actual configuration values."
        else
            print_error "No environment template found. Please create a .env file."
            exit 1
        fi
    else
        print_success "Environment file already exists."
    fi
}

# Function to build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml up --build -d
    
    print_success "Services started successfully."
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for web service
    print_status "Waiting for web service..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:5000/health >/dev/null 2>&1; then
            print_success "Web service is ready."
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Web service failed to start within 60 seconds."
        exit 1
    fi
    
    # Wait for database
    print_status "Waiting for database..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U marketing_user -d marketing_db >/dev/null 2>&1; then
            print_success "Database is ready."
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Database failed to start within 60 seconds."
        exit 1
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Initialize database tables
    docker-compose -f docker-compose.prod.yml exec -T web python -c "
import sys
sys.path.insert(0, 'src')
from main import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully.')
"
    
    print_success "Database migrations completed."
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    echo ""
    
    # Show running containers
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    print_status "Service URLs:"
    echo "  - Web Application: http://localhost:5000"
    echo "  - API Health Check: http://localhost:5000/health"
    echo "  - Grafana Dashboard: http://localhost:3000 (admin/admin)"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Neo4j Browser: http://localhost:7474"
    
    echo ""
    print_status "Useful Commands:"
    echo "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  - Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "  - Restart services: docker-compose -f docker-compose.prod.yml restart"
    echo "  - Scale web service: docker-compose -f docker-compose.prod.yml up --scale web=3 -d"
}

# Function to run tests
run_tests() {
    print_status "Running system tests..."
    
    # Test health endpoint
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        print_success "Health endpoint test passed."
    else
        print_error "Health endpoint test failed."
        exit 1
    fi
    
    # Test API endpoints
    if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
        print_success "API health endpoint test passed."
    else
        print_error "API health endpoint test failed."
        exit 1
    fi
    
    # Test agents endpoint
    if curl -f http://localhost:5000/api/agents/health >/dev/null 2>&1; then
        print_success "Agents health endpoint test passed."
    else
        print_error "Agents health endpoint test failed."
        exit 1
    fi
    
    print_success "All tests passed."
}

# Main deployment function
main() {
    echo "=========================================="
    echo "Multi-Agent Marketing System Deployment"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    setup_environment
    deploy_services
    wait_for_services
    run_migrations
    run_tests
    show_status
    
    echo ""
    print_success "Deployment completed successfully!"
    print_status "The system is now running and ready to use."
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose -f docker-compose.prod.yml down
        print_success "Services stopped."
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose -f docker-compose.prod.yml restart
        print_success "Services restarted."
        ;;
    "logs")
        docker-compose -f docker-compose.prod.yml logs -f
        ;;
    "status")
        show_status
        ;;
    "test")
        run_tests
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|test}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the complete system (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - View service logs"
        echo "  status  - Show deployment status"
        echo "  test    - Run system tests"
        exit 1
        ;;
esac
