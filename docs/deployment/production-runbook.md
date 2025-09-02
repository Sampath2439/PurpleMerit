# Production Deployment Guide

## Overview
This document outlines the deployment process for the AI-Enhanced Marketing Multi-Agent System in a production environment using Docker and Kubernetes.

## Prerequisites

### Infrastructure Requirements
- Kubernetes cluster 1.24+
- Container registry access
- OpenAI API key
- MongoDB cluster
- Redis cluster
- Neo4j instance

### Resource Requirements
Each agent pod requires:
- CPU: 250m (request) / 500m (limit)
- Memory: 512Mi (request) / 1Gi (limit)
- Storage: 20Gi per pod

## Configuration

### Environment Variables
1. Required API Keys:
   - `OPENAI_API_KEY`: OpenAI API key
   - `JWT_SECRET_KEY`: Secret for JWT token generation

2. Database Connections:
   - `MONGODB_URI`: MongoDB connection string
   - `REDIS_URI`: Redis connection string
   - `NEO4J_URI`: Neo4j connection string

### Kubernetes Secrets
```bash
kubectl create secret generic agent-secrets \
  --from-literal=OPENAI_API_KEY='your-api-key' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret' \
  --from-literal=MONGODB_URI='your-mongodb-uri' \
  --from-literal=REDIS_URI='your-redis-uri' \
  --from-literal=NEO4J_URI='your-neo4j-uri' \
  -n marketing-agents
```

## Deployment Steps

1. Create Namespace
```bash
kubectl apply -f deployment/kubernetes/namespace.yaml
```

2. Apply Configurations
```bash
kubectl apply -f deployment/kubernetes/configmap.yaml
kubectl apply -f deployment/kubernetes/secrets.yaml
```

3. Deploy Core Services
```bash
kubectl apply -f deployment/kubernetes/mcp-server-deployment.yaml
kubectl apply -f deployment/kubernetes/agents-deployment.yaml
kubectl apply -f deployment/kubernetes/services.yaml
```

4. Apply Network Policies
```bash
kubectl apply -f deployment/kubernetes/network-policies.yaml
```

5. Configure Autoscaling
```bash
kubectl apply -f deployment/kubernetes/hpa.yaml
```

## Monitoring

### Key Metrics
1. System Health
   - CPU/Memory usage
   - API response times
   - Error rates

2. AI Service Metrics
   - OpenAI API latency
   - Token usage
   - Model performance

3. Agent Metrics
   - Processing times
   - Queue lengths
   - Success rates

### Logging
Configure log aggregation to collect:
- Application logs
- AI service interactions
- Agent communications
- System events

## Scaling Considerations

### Horizontal Pod Autoscaling
- MCP Server: 3-10 replicas
- Agents: 3-10 replicas per type
- Scaling based on CPU (70%) and Memory (80%) utilization

### Resource Management
1. CPU Allocation:
   - Request: 250m
   - Limit: 500m

2. Memory Allocation:
   - Request: 512Mi
   - Limit: 1Gi

## Security

### Network Policies
- Restricted pod-to-pod communication
- Limited egress to essential services
- Secured OpenAI API access

### Authentication
- JWT-based API authentication
- Secure secret management
- Role-based access control

## Troubleshooting

### Common Issues
1. OpenAI API Issues
   ```bash
   kubectl logs deployment/agents -c engagement-agent
   kubectl describe pod -l app=agents
   ```

2. Memory Pressure
   ```bash
   kubectl top pods -n marketing-agents
   kubectl describe hpa agents-hpa
   ```

3. Network Issues
   ```bash
   kubectl describe networkpolicy agent-network-policy
   kubectl exec -it pod/mcp-server-xxx -- curl agents:8001/health
   ```

## Maintenance

### Updates and Rollouts
```bash
# Update agent images
kubectl set image deployment/agents \
  triage-agent=purplemerit/triage-agent:new-tag \
  engagement-agent=purplemerit/engagement-agent:new-tag \
  optimizer-agent=purplemerit/optimizer-agent:new-tag

# Monitor rollout
kubectl rollout status deployment/agents
```

### Backup Procedures
1. Database Backups
   - MongoDB snapshots
   - Redis persistence
   - Neo4j backups

2. Configuration Backups
   ```bash
   kubectl get -n marketing-agents \
     configmap,secret,deployment,service,networkpolicy,hpa \
     -o yaml > backup.yaml
   ```

## Support and Escalation
- Technical Support: tech-support@purplemerit.com
- Emergency Contact: oncall@purplemerit.com
- Documentation: https://docs.purplemerit.com

## System Overview
The Marketing Multi-Agent System consists of three specialized agents and supporting infrastructure:
- Lead Triage Agent
- Engagement Agent
- Campaign Optimization Agent

## Prerequisites
1. Kubernetes cluster (v1.24+)
2. Helm (v3.8+)
3. kubectl configured with cluster access
4. Docker registry access

## Deployment Steps

### 1. Environment Setup

```bash
# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Apply ConfigMap
kubectl apply -f kubernetes/configmap.yaml

# Apply Secrets
kubectl apply -f kubernetes/secrets.yaml
```

### 2. Infrastructure Components

```bash
# Deploy MongoDB
helm install mongodb bitnami/mongodb -f kubernetes/mongodb-values.yaml

# Deploy Redis
helm install redis bitnami/redis -f kubernetes/redis-values.yaml

# Deploy Neo4j for Knowledge Graph
helm install neo4j neo4j/neo4j -f kubernetes/neo4j-values.yaml
```

### 3. Core Services Deployment

```bash
# Deploy MCP Server
kubectl apply -f kubernetes/mcp-server-deployment.yaml
kubectl apply -f kubernetes/mcp-server-service.yaml

# Deploy Agents
kubectl apply -f kubernetes/agents-deployment.yaml

# Apply network policies
kubectl apply -f kubernetes/network-policies.yaml

# Configure HPA
kubectl apply -f kubernetes/hpa.yaml
```

### 4. Monitoring Setup

```bash
# Deploy Prometheus
helm install prometheus prometheus-community/prometheus

# Deploy Grafana
helm install grafana grafana/grafana

# Apply monitoring configuration
kubectl apply -f kubernetes/monitoring.yaml
```

## Health Checks

1. Verify MCP Server:
```bash
kubectl exec -it deploy/mcp-server -- curl localhost:8080/health
```

2. Check Agent Status:
```bash
kubectl get pods -l component=agents
kubectl logs -l component=agents
```

3. Monitor Resources:
```bash
kubectl top pods
kubectl top nodes
```

## Scaling Guidelines

### Horizontal Scaling
- Agents scale based on queue length
- MCP Server scales based on CPU/Memory
- Database connections adjust automatically

### Vertical Scaling
- Increase resource limits in deployment YAMLs
- Adjust HPA settings as needed
- Monitor resource utilization

## Troubleshooting

### Common Issues

1. Agent Connection Failures
```bash
# Check MCP Server logs
kubectl logs -l app=mcp-server

# Verify network policies
kubectl describe networkpolicy
```

2. Memory Pressure
```bash
# Check memory usage
kubectl top pods

# Adjust resource limits
kubectl edit deployment agents
```

3. Database Connectivity
```bash
# Test database connection
kubectl exec -it deploy/mcp-server -- python -c "
from mcp.db import test_connection
test_connection()
"
```

## Backup Procedures

1. Database Backups
```bash
# MongoDB backup
kubectl exec -it mongodb-0 -- mongodump

# Neo4j backup
kubectl exec -it neo4j-0 -- neo4j-admin dump
```

2. Configuration Backup
```bash
kubectl get configmap -o yaml > config-backup.yaml
kubectl get secrets -o yaml > secrets-backup.yaml
```

## Recovery Procedures

1. Database Recovery
```bash
# Restore MongoDB
kubectl exec -it mongodb-0 -- mongorestore

# Restore Neo4j
kubectl exec -it neo4j-0 -- neo4j-admin load
```

2. Configuration Recovery
```bash
kubectl apply -f config-backup.yaml
kubectl apply -f secrets-backup.yaml
```

## Monitoring & Alerts

### Key Metrics
1. Agent Performance
   - Queue length
   - Processing time
   - Success rate

2. System Health
   - CPU usage
   - Memory usage
   - Network latency

3. Business Metrics
   - Lead conversion rate
   - Campaign performance
   - Response time

### Alert Configuration
1. Critical Alerts
   - Agent failures
   - Database connectivity
   - High error rates

2. Warning Alerts
   - High latency
   - Queue buildup
   - Resource pressure

## Security Procedures

1. Access Control
   - Regular audit of RBAC
   - Certificate rotation
   - Secret management

2. Network Security
   - Network policy validation
   - TLS configuration
   - Ingress rules

3. Compliance Checks
   - Security scanning
   - Vulnerability assessment
   - Access logs review

## Maintenance Schedule

1. Regular Tasks
   - Log rotation: Daily
   - Metric cleanup: Weekly
   - Configuration review: Monthly

2. Periodic Updates
   - Security patches: As needed
   - Version updates: Quarterly
   - Infrastructure scaling: As needed

## Emergency Contacts

1. On-Call Team
   - Primary: [contact]
   - Secondary: [contact]
   - Manager: [contact]

2. External Support
   - Cloud Provider: [contact]
   - Database Support: [contact]
   - Security Team: [contact]
