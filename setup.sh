#!/bin/bash

# Global Brain Student Edition - Setup Script
# This script sets up the entire application stack

set -e

echo "🚀 Setting up Global Brain Student Edition..."

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

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. It's required for local development."
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 is not installed. It's required for local development."
    fi
    
    print_success "System requirements check completed"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# Global Brain Student Edition - Environment Configuration

# Application
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://globalbrain:globalbrain123@localhost:5432/globalbrain
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-change-in-production

# AI/LLM Services
OPENAI_API_KEY=your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=global-brain-embeddings

# AWS/S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-west-2
S3_BUCKET_NAME=global-brain-documents

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Email (for magic links)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
EOF
        print_success "Environment file created (.env)"
        print_warning "Please update the .env file with your actual API keys and configuration"
    else
        print_status "Environment file already exists"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Python virtual environment created"
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Backend dependencies installed"
    
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    print_success "Frontend dependencies installed"
    
    cd ..
}

# Setup mobile (Flutter)
setup_mobile() {
    print_status "Setting up mobile app..."
    
    cd mobile
    
    # Check if Flutter is installed
    if command -v flutter &> /dev/null; then
        flutter pub get
        print_success "Mobile dependencies installed"
    else
        print_warning "Flutter is not installed. Mobile app setup skipped."
        print_warning "Install Flutter from: https://flutter.dev/docs/get-started/install"
    fi
    
    cd ..
}

# Create Docker directories
create_docker_dirs() {
    print_status "Creating Docker configuration directories..."
    
    mkdir -p docker/nginx
    mkdir -p docker/postgres
    mkdir -p docker/prometheus
    mkdir -p docker/grafana/provisioning/datasources
    mkdir -p docker/grafana/provisioning/dashboards
    
    print_success "Docker directories created"
}

# Create Nginx configuration
create_nginx_config() {
    print_status "Creating Nginx configuration..."
    
    cat > docker/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://backend/health;
        }
    }
}
EOF
    
    print_success "Nginx configuration created"
}

# Create Prometheus configuration
create_prometheus_config() {
    print_status "Creating Prometheus configuration..."
    
    cat > docker/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'global-brain-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'global-brain-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
    
    print_success "Prometheus configuration created"
}

# Create Grafana datasource
create_grafana_datasource() {
    print_status "Creating Grafana datasource..."
    
    cat > docker/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    print_success "Grafana datasource created"
}

# Start services
start_services() {
    print_status "Starting services with Docker Compose..."
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "Services started successfully"
    print_status "Waiting for services to be ready..."
    
    # Wait for services to be ready
    sleep 30
    
    print_success "All services are ready!"
}

# Display access information
show_access_info() {
    print_success "Global Brain Student Edition is now running!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3001 (admin/admin)"
    echo ""
    echo "📱 Mobile App:"
    echo "   Run 'flutter run' in the mobile/ directory"
    echo ""
    echo "🔧 Development:"
    echo "   Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "   Frontend: cd frontend && npm run dev"
    echo ""
    echo "📊 Monitoring:"
    echo "   Logs: docker-compose logs -f [service-name]"
    echo "   Stop: docker-compose down"
    echo "   Restart: docker-compose restart"
}

# Main setup function
main() {
    echo "🎓 Global Brain Student Edition Setup"
    echo "====================================="
    echo ""
    
    check_requirements
    create_env_file
    create_docker_dirs
    create_nginx_config
    create_prometheus_config
    create_grafana_datasource
    
    # Ask user if they want to set up local development environment
    read -p "Do you want to set up local development environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_backend
        setup_frontend
        setup_mobile
    fi
    
    # Ask user if they want to start services
    read -p "Do you want to start the services now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
        show_access_info
    else
        echo ""
        print_status "To start services later, run: docker-compose up -d"
    fi
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    print_warning "Don't forget to:"
    echo "   1. Update the .env file with your API keys"
    echo "   2. Configure your AWS S3 bucket"
    echo "   3. Set up Pinecone vector database"
    echo "   4. Configure email settings for magic links"
}

# Run main function
main "$@"