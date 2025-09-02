# Grafana Dashboard Access Guide

This guide explains how to access and use the Grafana dashboards for monitoring the Multi-Agent Marketing System.

## Quick Start

### 1. Start the Monitoring Stack
```bash
# Start the full stack with monitoring
docker-compose -f docker-compose.yml up -d

# Or start just the monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Access Grafana
- **URL**: `http://localhost:3000`
- **Username**: `admin`
- **Password**: `admin` (or check docker-compose file for actual password)

## Detailed Setup

### Docker Compose Configuration
The application includes Grafana in the Docker Compose configuration with the following services:

- **Grafana**: Web-based monitoring dashboard
- **Prometheus**: Metrics collection and storage
- **Alertmanager**: Alert management
- **Node Exporter**: System metrics collection

### Port Configuration
The monitoring stack uses these ports:

| Service | Port | Description |
|---------|------|-------------|
| Grafana | 3000 | Web dashboard interface |
| Prometheus | 9090 | Metrics collection |
| Alertmanager | 9093 | Alert management |
| Node Exporter | 9100 | System metrics |

## Grafana Configuration

### Pre-configured Dashboards
The system includes several pre-built dashboards located in `monitoring/grafana/dashboards/`:

1. **System Overview**
   - General system health and performance
   - CPU, memory, and disk usage
   - Service status and uptime

2. **Agent Performance**
   - Multi-agent system metrics
   - Agent response times
   - Handoff success rates
   - Agent utilization

3. **API Metrics**
   - Flask API performance
   - Request/response times
   - Error rates and status codes
   - Endpoint usage statistics

4. **Database Metrics**
   - Database performance
   - Query execution times
   - Connection pool status
   - Database size and growth

5. **Memory Usage**
   - System memory utilization
   - Application memory usage
   - Cache performance (Redis)
   - Memory leaks detection

### Data Sources
Grafana is pre-configured to pull data from:

- **Prometheus**: Primary metrics collection
- **PostgreSQL**: Database performance metrics
- **Redis**: Cache performance metrics
- **Application Metrics**: Custom business metrics

## Access Steps

### Step 1: Start Services
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services are running
docker-compose -f docker-compose.monitoring.yml ps
```

### Step 2: Wait for Initialization
Wait approximately 30-60 seconds for all services to fully initialize.

### Step 3: Access Grafana
1. Open your web browser
2. Navigate to: `http://localhost:3000`
3. Login with:
   - Username: `admin`
   - Password: `admin`

### Step 4: Navigate Dashboards
1. Click on the "Dashboards" icon in the left sidebar
2. Browse available dashboards
3. Click on any dashboard to view it

## Dashboard Features

### Real-time Monitoring
- **Live metrics** from the multi-agent system
- **Real-time updates** every 5-15 seconds
- **Interactive charts** with zoom and pan capabilities

### Key Metrics Tracked
- **Agent Performance**:
  - Response times per agent
  - Success/failure rates
  - Handoff efficiency
  - Queue lengths

- **API Performance**:
  - Request latency
  - Throughput (requests/second)
  - Error rates
  - Status code distribution

- **System Resources**:
  - CPU utilization
  - Memory usage
  - Disk I/O
  - Network traffic

- **Business Metrics**:
  - Lead processing rates
  - Campaign performance
  - User engagement
  - Conversion rates

## Troubleshooting

### Common Issues

#### 1. Cannot Access Grafana (Port 3000)
```bash
# Check if port is in use
netstat -an | grep 3000

# Check container status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs grafana
```

#### 2. Services Not Starting
```bash
# Check Docker daemon
docker info

# Check available resources
docker system df

# Restart services
docker-compose -f docker-compose.monitoring.yml down
docker-compose -f docker-compose.monitoring.yml up -d
```

#### 3. No Data in Dashboards
```bash
# Check Prometheus connection
curl http://localhost:9090/api/v1/targets

# Check application metrics
curl http://localhost:5000/metrics

# Verify data sources in Grafana
# Go to Configuration > Data Sources
```

#### 4. Authentication Issues
- Check the actual password in `docker-compose.monitoring.yml`
- Look for `GF_SECURITY_ADMIN_PASSWORD` environment variable
- Reset password if needed:
  ```bash
  docker exec -it grafana_container grafana-cli admin reset-admin-password newpassword
  ```

### Log Analysis
```bash
# View Grafana logs
docker-compose -f docker-compose.monitoring.yml logs grafana

# View Prometheus logs
docker-compose -f docker-compose.monitoring.yml logs prometheus

# View all monitoring logs
docker-compose -f docker-compose.monitoring.yml logs
```

## Customization

### Adding New Dashboards
1. **Create Dashboard**:
   - Click "+" in Grafana sidebar
   - Select "Dashboard"
   - Add panels and configure metrics

2. **Import Dashboard**:
   - Go to "+" > "Import"
   - Upload JSON dashboard file
   - Configure data sources

### Setting Up Alerts
1. **Create Alert Rules**:
   - Go to "Alerting" > "Alert Rules"
   - Define conditions and thresholds
   - Set notification channels

2. **Configure Notifications**:
   - Set up email, Slack, or webhook notifications
   - Define alert severity levels
   - Configure escalation policies

### Custom Metrics
To add custom business metrics:

1. **Instrument Application**:
   ```python
   from prometheus_client import Counter, Histogram
   
   # Define custom metrics
   leads_processed = Counter('leads_processed_total', 'Total leads processed')
   campaign_performance = Histogram('campaign_roas', 'Campaign ROAS distribution')
   ```

2. **Expose Metrics Endpoint**:
   ```python
   # Add to Flask app
   from prometheus_client import generate_latest
   
   @app.route('/metrics')
   def metrics():
       return generate_latest()
   ```

3. **Configure Prometheus**:
   - Add scrape configuration
   - Reload Prometheus configuration

## Security Considerations

### Production Deployment
- **Change default passwords**
- **Enable HTTPS** for Grafana
- **Configure authentication** (LDAP, OAuth)
- **Set up proper firewall rules**
- **Use secrets management** for credentials

### Access Control
- **Create user roles** with appropriate permissions
- **Limit dashboard access** based on user roles
- **Audit user activities**
- **Set up session timeouts**

## Best Practices

### Dashboard Design
- **Keep dashboards focused** on specific use cases
- **Use consistent color schemes** and layouts
- **Include context** and explanations
- **Optimize for different screen sizes**

### Performance
- **Limit time ranges** for large datasets
- **Use appropriate refresh intervals**
- **Optimize queries** and aggregations
- **Monitor Grafana performance**

### Maintenance
- **Regular backup** of dashboard configurations
- **Update Grafana** and plugins regularly
- **Monitor disk usage** for metrics storage
- **Review and clean up** old metrics

## Support

### Getting Help
1. **Check logs** for error messages
2. **Review documentation** for Grafana and Prometheus
3. **Check community forums** for common issues
4. **Contact system administrator** for infrastructure issues

### Useful Commands
```bash
# Restart monitoring stack
docker-compose -f docker-compose.monitoring.yml restart

# Update monitoring stack
docker-compose -f docker-compose.monitoring.yml pull
docker-compose -f docker-compose.monitoring.yml up -d

# Clean up old data
docker system prune -f

# Backup Grafana data
docker cp grafana_container:/var/lib/grafana ./grafana-backup
```

## Next Steps

After accessing Grafana:

1. **Explore pre-built dashboards**
2. **Customize dashboards** for your needs
3. **Set up alerts** for critical metrics
4. **Create custom dashboards** for specific use cases
5. **Configure notifications** for important events
6. **Monitor system performance** regularly
7. **Optimize based on insights** from the data

The Grafana setup provides comprehensive monitoring capabilities for the Multi-Agent Marketing System with minimal configuration required.
