# Multi-Agent Marketing System - Deployment Guide

This guide covers deploying the Multi-Agent Marketing System in various environments.

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.11+
- pip
- Virtual environment support

### Local Development Setup

1. **Clone and setup**:
   ```bash
   git clone <repository_url>
   cd multi_agent_marketing_system
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   # Option 1: Use the startup script
   python start.py
   
   # Option 2: Run directly
   cd src
   python main.py
   ```

5. **Access the system**:
   - Dashboard: http://localhost:5000
   - API: http://localhost:5000/api
   - Health check: http://localhost:5000/health

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Check service status**:
   ```bash
   docker-compose ps
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f app
   ```

4. **Stop services**:
   ```bash
   docker-compose down
   ```

### Individual Docker Services

- **Main App**: http://localhost:5000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Neo4j**: http://localhost:7474
- **MCP Server**: ws://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## ☁️ Production Deployment

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port

# Agent Configuration
MAX_CONCURRENT_AGENTS=20
AGENT_TIMEOUT_SECONDS=300

# Security Configuration
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# MCP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8080
```

### Production Docker Deployment

1. **Build production image**:
   ```bash
   docker build -t marketing-system:latest .
   ```

2. **Run with production config**:
   ```bash
   docker run -d \
     --name marketing-system \
     -p 5000:5000 \
     --env-file .env \
     marketing-system:latest
   ```

### Kubernetes Deployment

1. **Create namespace**:
   ```bash
   kubectl create namespace marketing-system
   ```

2. **Apply configurations**:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secrets.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

3. **Check deployment status**:
   ```bash
   kubectl get pods -n marketing-system
   kubectl get services -n marketing-system
   ```

## 🔧 Configuration

### Development Configuration

```python
# config.py
from config import DevelopmentConfig

app.config.from_object(DevelopmentConfig)
```

### Production Configuration

```python
# config.py
from config import ProductionConfig

app.config.from_object(ProductionConfig)
```

### Custom Configuration

```python
# config.py
class CustomConfig(Config):
    # Override specific settings
    MAX_CONCURRENT_AGENTS = 50
    AGENT_TIMEOUT_SECONDS = 600
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints

- **System Health**: `GET /health`
- **Agent Health**: `GET /api/agents/health`
- **User Service Health**: `GET /api/health`

### Metrics Endpoints

- **Prometheus Metrics**: `GET /metrics`
- **Agent Performance**: `GET /api/agents/analytics/performance`
- **System Status**: `GET /api/agents/system/status`

### Logging

The system uses structured logging with configurable levels:

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Log format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔒 Security Configuration

### Authentication

- JWT-based authentication
- Token expiration configurable
- Role-based access control (RBAC)

### CORS Configuration

```python
# Configure CORS origins
CORS_ORIGINS = [
    'https://yourdomain.com',
    'https://app.yourdomain.com'
]

# Enable CORS
CORS(app, origins=CORS_ORIGINS)
```

### Rate Limiting

```python
# Enable rate limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 1000  # requests per window
RATE_LIMIT_WINDOW = 3600    # seconds
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check database service is running
   - Verify connection string
   - Check firewall settings

2. **Agent Not Responding**:
   - Check agent logs
   - Verify MCP server connection
   - Check resource limits

3. **Memory Issues**:
   - Monitor memory usage
   - Adjust memory limits
   - Check for memory leaks

### Debug Mode

Enable debug mode for development:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f app

# View specific service logs
docker-compose logs -f mcp_server

# Search logs for errors
docker-compose logs app | grep ERROR
```

## 📈 Scaling

### Horizontal Scaling

1. **Scale application instances**:
   ```bash
   docker-compose up -d --scale app=3
   ```

2. **Load balancer configuration**:
   ```nginx
   upstream marketing_system {
       server app1:5000;
       server app2:5000;
       server app3:5000;
   }
   ```

### Vertical Scaling

Adjust resource limits in docker-compose.yml:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
```

## 🔄 Updates & Maintenance

### Rolling Updates

```bash
# Update application
docker-compose pull
docker-compose up -d --no-deps app

# Rollback if needed
docker-compose up -d --no-deps app:previous
```

### Database Migrations

```bash
# Run migrations
docker-compose exec app python manage.py db upgrade

# Create new migration
docker-compose exec app python manage.py db migrate -m "Description"
```

### Backup & Recovery

```bash
# Database backup
docker-compose exec db pg_dump -U postgres marketing_system > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres marketing_system < backup.sql
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🆘 Support

For deployment issues:

1. Check the logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Check service status: `docker-compose ps`
4. Review this deployment guide
5. Check the main README.md for additional information

---

**Happy Deploying! 🚀**

