# 🚀 Multi-Agent Marketing System - Quick Start Guide

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **Git** (for cloning the repository)
- **4GB+ RAM** available for Docker containers
- **Ports 5000, 3000, 5432, 6379, 7474, 9090** available

## ⚡ Quick Deployment (5 Minutes)

### Option 1: Using Deployment Scripts

**Windows:**
```cmd
# Clone the repository
git clone <repository_url>
cd multi_agent_marketing_system

# Run deployment script
deploy.bat
```

**Linux/Mac:**
```bash
# Clone the repository
git clone <repository_url>
cd multi_agent_marketing_system

# Make script executable and run
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Docker Commands

```bash
# 1. Setup environment
cp env.template .env
# Edit .env file with your configuration

# 2. Start all services
docker-compose -f docker-compose.prod.yml up --build -d

# 3. Wait for services to be ready (30-60 seconds)
# Check status
docker-compose -f docker-compose.prod.yml ps

# 4. Test the system
curl http://localhost:5000/health
```

## 🌐 Access Your System

Once deployed, access these URLs:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:5000 | - |
| **API Health** | http://localhost:5000/health | - |
| **Grafana Monitoring** | http://localhost:3000 | admin/admin |
| **Prometheus Metrics** | http://localhost:9090 | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j/your-password |

## 🧪 Test the System

### 1. Test Lead Triage Agent
```bash
curl -X POST http://localhost:5000/api/agents/triage \
  -H "Content-Type: application/json" \
  -d '{
    "lead_data": {
      "lead_id": "TEST_001",
      "company_name": "Test Company",
      "industry": "SaaS",
      "company_size": "201-1000",
      "persona": "CMO",
      "region": "US",
      "source": "Website"
    }
  }'
```

### 2. Test Engagement Agent
```bash
curl -X POST http://localhost:5000/api/agents/engage \
  -H "Content-Type: application/json" \
  -d '{
    "lead_data": {
      "lead_id": "TEST_002",
      "company_name": "Test Company 2",
      "industry": "FinTech"
    },
    "engagement_type": "welcome"
  }'
```

### 3. Test Campaign Optimization
```bash
curl -X POST http://localhost:5000/api/agents/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_data": {
      "campaign_id": "CAMP_001",
      "campaign_name": "Test Campaign",
      "ctr": 0.025,
      "cpl_usd": 75.0,
      "roas": 1.8
    },
    "optimization_type": "performance_check"
  }'
```

## 🔧 Configuration

### Environment Variables (.env file)

Key settings to configure:

```bash
# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-change-this
POSTGRES_PASSWORD=your-secure-database-password
REDIS_PASSWORD=your-secure-redis-password
NEO4J_PASSWORD=your-secure-neo4j-password

# Optional: External Services
OPENAI_API_KEY=your-openai-api-key
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f db
```

### System Status
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check resource usage
docker stats

# Health checks
curl http://localhost:5000/health
curl http://localhost:5000/api/agents/health
```

## 🛠️ Management Commands

### Start/Stop Services
```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Scale web service (3 instances)
docker-compose -f docker-compose.prod.yml up --scale web=3 -d
```

### Database Operations
```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U marketing_user marketing_db > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U marketing_user marketing_db < backup.sql

# Access database shell
docker-compose -f docker-compose.prod.yml exec db psql -U marketing_user marketing_db
```

### Updates and Maintenance
```bash
# Update and rebuild
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d

# Clean up unused resources
docker system prune -a

# View disk usage
docker system df
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port
netstat -tulpn | grep :5000
# Kill process
kill -9 <PID>
```

**2. Services Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Check Docker resources
docker system df
```

**3. Database Connection Issues**
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Reset database
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

**4. Memory Issues**
```bash
# Check memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

### Performance Optimization

**1. Increase Resources**
- Docker Desktop: Settings → Resources → Memory (increase to 4GB+)
- Docker Desktop: Settings → Resources → CPUs (increase to 2+)

**2. Optimize Database**
```bash
# Access database and run optimization
docker-compose -f docker-compose.prod.yml exec db psql -U marketing_user marketing_db
# Run: VACUUM ANALYZE;
```

**3. Enable Caching**
- Redis is already configured for caching
- Check Redis status: `docker-compose -f docker-compose.prod.yml exec redis redis-cli ping`

## 🔒 Security Checklist

- [ ] Change all default passwords in `.env` file
- [ ] Use strong, unique passwords
- [ ] Enable HTTPS in production (uncomment nginx SSL config)
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup data regularly

## 📈 Production Deployment

### 1. Production Environment Setup
```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key

# Use production database
export DATABASE_URL=postgresql://user:password@prod-db:5432/marketing_db
```

### 2. SSL/HTTPS Configuration
1. Obtain SSL certificates
2. Place certificates in `nginx/ssl/` directory
3. Uncomment HTTPS configuration in `nginx/nginx.conf`
4. Update DNS to point to your server

### 3. Scaling for High Traffic
```bash
# Scale web service
docker-compose -f docker-compose.prod.yml up --scale web=5 -d

# Use load balancer (nginx is already configured)
# Consider using cloud load balancer for high availability
```

## 📞 Support

### Getting Help
1. **Check Logs**: `docker-compose -f docker-compose.prod.yml logs -f`
2. **System Status**: `docker-compose -f docker-compose.prod.yml ps`
3. **Health Checks**: Visit http://localhost:5000/health
4. **Documentation**: See `SYSTEM_ARCHITECTURE.md` for detailed information

### Useful Resources
- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

## 🎯 Next Steps

1. **Explore the Dashboard**: Visit http://localhost:5000
2. **Test Agent Functions**: Use the interactive test buttons
3. **Monitor Performance**: Check Grafana dashboard at http://localhost:3000
4. **Customize Configuration**: Edit `.env` file for your needs
5. **Add Your Data**: Import your marketing data into the system
6. **Scale as Needed**: Add more agent instances for higher throughput

---

**🎉 Congratulations!** Your Multi-Agent Marketing System is now running and ready to process leads, manage engagements, and optimize campaigns automatically!
