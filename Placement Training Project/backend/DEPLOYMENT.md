# Deployment Guide - Dynamic Pricing Engine

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Platform Deployment](#cloud-platform-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Performance Optimization](#performance-optimization)

---

## Local Development

### Prerequisites
- Python 3.8+
- pip or conda
- Git (optional)

### Setup Steps

```bash
# 1. Clone or navigate to project
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
copy .env.example .env
# Edit .env if needed

# 6. Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will run at:** `http://localhost:8000`

---

## Docker Deployment

### Build Docker Image

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs config app/models

# Expose port
EXPOSE 8000

# Set environment
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t dynamic-pricing-engine:latest .

# Run container
docker run -p 8000:8000 \
  -e API_PORT=8000 \
  -e DEBUG=false \
  -v $(pwd)/logs:/app/logs \
  dynamic-pricing-engine:latest

# For Windows:
docker run -p 8000:8000 ^
  -e API_PORT=8000 ^
  -e DEBUG=false ^
  -v %cd%/logs:/app/logs ^
  dynamic-pricing-engine:latest
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      API_HOST: 0.0.0.0
      API_PORT: 8000
      DEBUG: "false"
      LOG_LEVEL: INFO
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Run with Docker Compose:
```bash
docker-compose up -d
```

---

## Cloud Platform Deployment

### AWS Elastic Container Service (ECS)

1. **Create ECR Repository:**
   ```bash
   aws ecr create-repository --repository-name dynamic-pricing-engine
   ```

2. **Push Docker Image:**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker tag dynamic-pricing-engine:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing-engine:latest
   
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dynamic-pricing-engine:latest
   ```

3. **Create ECS Task Definition** (update image URI)

4. **Deploy to ECS Cluster**

### AWS Lambda + API Gateway

1. **Prepare for Lambda:**
   ```bash
   pip install -r requirements.txt -t package/
   cp -r app package/
   cd package && zip -r ../deployment.zip . && cd ..
   ```

2. **Use serverless-http wrapper:**
   ```python
   from mangum import Mangum
   from app.main import app
   handler = Mangum(app)
   ```

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy dynamic-pricing-engine \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --allow-unauthenticated
```

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create dynamic-pricing-engine

# Set environment variables
heroku config:set API_PORT=8000

# Deploy
git push heroku main
```

### Azure App Service

```bash
# Create resource group
az group create --name pricing-engine-rg --location eastus

# Create app service plan
az appservice plan create --name pricing-engine-plan --resource-group pricing-engine-rg --sku B2

# Create web app
az webapp create --resource-group pricing-engine-rg --plan pricing-engine-plan --name dynamic-pricing-engine

# Deploy from local git
az webapp up --resource-group pricing-engine-rg --name dynamic-pricing-engine
```

---

## Production Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
DEBUG=false
LOG_LEVEL=WARNING

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Firebase
FIREBASE_CREDENTIALS_PATH=/run/secrets/firebase_creds.json
ENABLE_FIREBASE=true
ENABLE_ANALYTICS=true

# Security
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600
```

### Nginx Configuration

```nginx
upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Cache static content
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
    }
}
```

---

## Monitoring & Logging

### Application Monitoring

```python
# Add to app/main.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def add_metrics(request, call_next):
    request_count.inc()
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    request_duration.observe(duration)
    return response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest())
```

### Logging Configuration

Configure `logs/`:
- Separate logs for different components
- Rotation and retention policies
- Centralized logging (ELK, Splunk, etc.)

### Uptime Monitoring

```bash
# Health check endpoint (add to monitoring service)
curl -f http://yourdomain.com/api/health || alert
```

---

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from cachetools import TTLCache

# Cache with 1-hour TTL
cache = TTLCache(maxsize=1000, ttl=3600)

@app.get("/cached-endpoint")
async def cached_endpoint(product_id: str):
    if product_id in cache:
        return cache[product_id]
    
    result = expensive_operation(product_id)
    cache[product_id] = result
    return result
```

### Database Connection Pooling

```python
# For Firebase (handled automatically)
# For additional databases, use connection pools:
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/db',
                      pool_size=20,
                      max_overflow=40)
```

### Load Testing

```bash
# Install Apache Bench or locust
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### Auto-scaling Configuration

**Docker Swarm:**
```bash
docker service create --name api \
  --replicas 3 \
  --update-parallelism 1 \
  --update-delay 10s \
  dynamic-pricing-engine:latest
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynamic-pricing-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pricing-api
  template:
    metadata:
      labels:
        app: pricing-api
    spec:
      containers:
      - name: api
        image: dynamic-pricing-engine:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

---

## Checklist for Production Deployment

- [ ] Environment variables configured
- [ ] Database backups configured
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Database connection pooling configured
- [ ] Logs centralized
- [ ] Auto-scaling configured
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Disaster recovery plan in place

---

## Support & Troubleshooting

### Container Won't Start
```bash
docker logs <container-id>
```

### High Memory Usage
- Increase container memory
- Reduce model batch size
- Enable caching

### Slow Responses
- Check database connection pooling
- Enable Redis caching
- Optimize queries
- Add load balancing

---

For more information, refer to [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)
