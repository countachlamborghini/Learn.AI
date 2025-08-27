# Global Brain Student Edition - Deployment Guide

This guide covers deploying the Global Brain Student Edition application to various environments.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)
- Flutter SDK (for mobile development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd global-brain-student-edition
./setup.sh
```

### 2. Configure Environment

Edit the `.env` file with your actual API keys and configuration:

```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-west-2
S3_BUCKET_NAME=your-s3-bucket-name

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### 3. Start Services

```bash
docker-compose up -d
```

## 🌐 Production Deployment

### Option 1: Docker Compose (Recommended for small to medium scale)

1. **Prepare Production Environment**

```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Create production .env
cp .env.example .env.prod
# Edit .env.prod with production values
```

2. **Deploy with Docker Compose**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Kubernetes (Recommended for large scale)

1. **Create Kubernetes Cluster**

```bash
# Using minikube for local testing
minikube start

# Or use cloud provider (AWS EKS, GKE, Azure AKS)
```

2. **Deploy with Helm**

```bash
# Install Helm charts
helm install global-brain ./helm/global-brain
```

3. **Configure Ingress**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: global-brain-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: global-brain-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

### Option 3: Cloud Platform Deployment

#### AWS Deployment

1. **Using AWS ECS with Fargate**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name global-brain

# Deploy using AWS CLI or AWS Console
aws ecs create-service \
  --cluster global-brain \
  --service-name global-brain-service \
  --task-definition global-brain-task \
  --desired-count 2
```

2. **Using AWS App Runner**

```bash
# Deploy backend
aws apprunner create-service \
  --source-configuration file://backend-source-config.json \
  --instance-configuration file://instance-config.json

# Deploy frontend
aws apprunner create-service \
  --source-configuration file://frontend-source-config.json \
  --instance-configuration file://instance-config.json
```

#### Google Cloud Platform

1. **Using Cloud Run**

```bash
# Deploy backend
gcloud run deploy global-brain-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy global-brain-frontend \
  --source ./frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

2. **Using GKE (Google Kubernetes Engine)**

```bash
# Create GKE cluster
gcloud container clusters create global-brain-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

# Deploy application
kubectl apply -f k8s/
```

## 📱 Mobile App Deployment

### Android

1. **Build APK**

```bash
cd mobile
flutter build apk --release
```

2. **Upload to Google Play Console**

```bash
# Generate signed APK
flutter build appbundle --release

# Upload to Google Play Console
# Follow Google Play Console instructions
```

### iOS

1. **Build iOS App**

```bash
cd mobile
flutter build ios --release
```

2. **Upload to App Store Connect**

```bash
# Archive and upload using Xcode
# Or use fastlane for automation
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Application environment | Yes | `development` |
| `DEBUG` | Debug mode | No | `true` |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `PINECONE_API_KEY` | Pinecone API key | Yes | - |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes | - |
| `S3_BUCKET_NAME` | S3 bucket name | Yes | - |
| `SECRET_KEY` | Application secret key | Yes | - |
| `JWT_SECRET` | JWT signing secret | Yes | - |

### Database Setup

1. **PostgreSQL**

```sql
-- Create database
CREATE DATABASE globalbrain;

-- Create user
CREATE USER globalbrain WITH PASSWORD 'your-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE globalbrain TO globalbrain;
```

2. **Redis**

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### External Services Setup

#### OpenAI

1. Create account at [OpenAI](https://openai.com)
2. Generate API key
3. Add to environment variables

#### Pinecone

1. Create account at [Pinecone](https://pinecone.io)
2. Create index with dimension 1536
3. Get API key and environment
4. Add to environment variables

#### AWS S3

1. Create S3 bucket
2. Configure CORS policy
3. Create IAM user with S3 access
4. Add credentials to environment variables

## 📊 Monitoring and Observability

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:

- Request duration
- Error rates
- Database connection pool
- Cache hit rates
- AI model usage

### Grafana Dashboards

Access Grafana at `http://your-domain:3001`:

- Application metrics
- User activity
- AI model performance
- System resources

### Logging

```bash
# View logs
docker-compose logs -f [service-name]

# Log aggregation with ELK stack
# Configure logstash to collect logs
```

## 🔒 Security

### SSL/TLS Configuration

1. **Using Let's Encrypt**

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx
sudo nano /etc/nginx/sites-available/global-brain
```

2. **Using Cloud Load Balancer**

```bash
# AWS ALB
aws elbv2 create-load-balancer \
  --name global-brain-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Configure SSL certificate
aws acm import-certificate \
  --certificate fileb://certificate.pem \
  --private-key fileb://private-key.pem
```

### Security Headers

```nginx
# Nginx security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 🚀 Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with Kubernetes
kubectl scale deployment backend --replicas=5
```

### Database Scaling

1. **Read Replicas**

```sql
-- Configure read replicas
-- Update application to use read replicas for queries
```

2. **Connection Pooling**

```python
# Configure connection pooling
DATABASE_URL = "postgresql://user:pass@host:port/db?pool_size=20&max_overflow=30"
```

### Caching Strategy

```python
# Redis caching configuration
CACHE_CONFIG = {
    'default': {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': 'redis://localhost:6379/0',
        'CACHE_DEFAULT_TIMEOUT': 300
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy Global Brain

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend && python -m pytest
          cd frontend && npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

### GitLab CI

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - cd backend && python -m pytest
    - cd frontend && npm test

build:
  stage: build
  script:
    - docker build -t global-brain-backend ./backend
    - docker build -t global-brain-frontend ./frontend

deploy:
  stage: deploy
  script:
    - docker-compose -f docker-compose.prod.yml up -d
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Issues**

```bash
# Check database connectivity
docker-compose exec backend python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:pass@host:5432/db')
print('Connected successfully')
"
```

2. **Redis Connection Issues**

```bash
# Test Redis connection
docker-compose exec backend python -c "
import redis
r = redis.Redis(host='redis', port=6379)
print(r.ping())
"
```

3. **AI Service Issues**

```bash
# Test OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Performance Optimization

1. **Database Optimization**

```sql
-- Create indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_mastery_user_topic ON mastery(user_id, topic);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM documents WHERE user_id = 1;
```

2. **Caching Optimization**

```python
# Implement caching for expensive operations
@cache.memoize(timeout=300)
def get_user_progress(user_id):
    # Expensive database query
    pass
```

3. **Frontend Optimization**

```javascript
// Implement code splitting
const Dashboard = lazy(() => import('./Dashboard'));
const Documents = lazy(() => import('./Documents'));

// Optimize bundle size
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
    },
  },
};
```

## 📞 Support

For deployment support:

- Check the [GitHub Issues](https://github.com/your-repo/issues)
- Review the [Documentation](https://docs.globalbrain.com)
- Contact the development team

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.