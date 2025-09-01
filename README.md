# Multi-Agent Marketing System

A production-ready, scalable multi-agent marketing automation system implementing sophisticated lead triage, engagement, and campaign optimization capabilities with adaptive memory and MCP (Model Context Protocol) integration.

## 🚀 Overview

This system implements a comprehensive multi-agent architecture designed to autonomously manage marketing operations through three specialized agents:

- **Lead Triage Agent**: Categorizes and scores incoming leads using machine learning models
- **Engagement Agent**: Manages personalized multi-channel outreach and communication
- **Campaign Optimization Agent**: Monitors and optimizes campaign performance using data-driven strategies

## 🏗️ Architecture

The system follows a microservices architecture with the following key components:

- **Agent Layer**: Three specialized agents with distinct responsibilities
- **Memory Architecture**: Multi-layered memory system (short-term, long-term, episodic, semantic)
- **Communication Layer**: MCP-based secure inter-agent communication
- **Data Layer**: Comprehensive marketing data management with ML pipeline
- **API Gateway**: RESTful API endpoints for external integration
- **Monitoring & Analytics**: Real-time system performance tracking

## 📋 Features

### Core Capabilities
- ✅ Automated lead classification and scoring
- ✅ Multi-channel engagement (Email, SMS, Social, Web, Call)
- ✅ Real-time campaign performance monitoring
- ✅ A/B testing and optimization
- ✅ Adaptive learning through memory systems
- ✅ Secure MCP-based communication
- ✅ Comprehensive API endpoints
- ✅ Production-ready deployment configuration

### Advanced Features
- ✅ Machine learning-based lead scoring
- ✅ Personalized content generation
- ✅ Statistical significance testing for A/B variants
- ✅ Multi-armed bandit algorithms for budget allocation
- ✅ Knowledge graph for semantic understanding
- ✅ Comprehensive test suite with edge case handling
- ✅ Scalable architecture supporting 10x load increase

## 🛠️ Technology Stack

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Machine Learning**: scikit-learn, pandas, numpy
- **Communication**: WebSockets, JSON-RPC 2.0
- **Database**: SQLite (development), PostgreSQL (production)
- **Caching**: Redis
- **Graph Database**: Neo4j
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Testing**: unittest, asyncio
- **Production Server**: Gunicorn with gevent workers

## 📁 Project Structure

```
multi_agent_marketing_system/
├── src/
│   ├── agents.py              # Agent implementations & orchestrator
│   ├── main.py                # Flask application entry point
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── mcp_server.py      # MCP server implementation (WebSocket/HTTP)
│   ├── mcp_server.py          # Alternative MCP server implementation
│   ├── routes/
│   │   ├── agents.py          # Agent API endpoints
│   │   └── user.py            # User management endpoints
│   ├── models/
│   │   └── user.py            # Database models
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_processing.py # Data processing, ML pipeline, memory system
│   ├── static/                # Frontend assets
│   │   ├── index.html         # Main dashboard
│   │   └── app.js             # Frontend JavaScript
│   └── tests.py               # Comprehensive test suite
├── data/                      # Marketing data files (CSV samples)
├── database/                  # Database files
│   ├── app.db                 # SQLite database (auto-created)
│   └── init.sql               # PostgreSQL initialization
├── monitoring/                # Prometheus & Grafana configs
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       └── datasources/
├── nginx/                     # Nginx configuration
│   ├── nginx.conf
│   └── ssl/                   # SSL certificates (production)
├── venv/                      # Python virtual environment
├── requirements.txt           # Python dependencies
├── start.py                   # Startup script for local development
├── docker-compose.yml         # Development Docker setup
├── docker-compose.prod.yml    # Production Docker setup
├── Dockerfile                 # Production Docker image
├── deploy.bat                 # Windows deployment script
├── deploy.sh                  # Linux/Mac deployment script
├── README.md                  # This file
├── QUICK_START.md             # Quick deployment guide
├── DEPLOYMENT.md              # Detailed deployment guide
├── SYSTEM_ARCHITECTURE.md     # System architecture guide
└── BACKEND_OVERVIEW.md        # Backend implementation details
```

## 🚀 Quick Start

### Option 1: Local Development (Recommended for first-time users)

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd multi_agent_marketing_system
   ```

2. **Run the startup script**:
   ```bash
   # Windows
   python start.py
   
   # Linux/Mac
   python3 start.py
   ```

   This will:
   - Create a virtual environment if needed
   - Install all dependencies
   - Start the Flask application
   - Open http://localhost:5000

### Option 2: Manual Setup

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python src/main.py
   ```

### Option 3: Docker Deployment

1. **Start all services**:
   ```bash
   # Development
   docker compose up -d
   
   # Production
   docker compose -f docker-compose.prod.yml up -d
   ```

2. **Access the system**:
   - Main App: http://localhost:5000
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Neo4j: http://localhost:7474

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Frontend dashboard
- `GET /health` - System health check
- `GET /api/health` - User service health
- `GET /api/agents/health` - Agent system health

### Agent Operations
- `POST /api/agents/triage` - Lead triage processing
- `POST /api/agents/engage` - Lead engagement
- `POST /api/agents/optimize` - Campaign optimization
- `POST /api/agents/handoff` - Agent handoff execution

### Memory Management
- `POST /api/agents/memory/store` - Store agent memory
- `GET /api/agents/memory/retrieve` - Retrieve agent memory

### Analytics
- `GET /api/agents/analytics/performance` - Performance analytics
- `POST /api/agents/data/process` - Data processing pipeline
- `POST /api/agents/predict/lead_score` - Lead score prediction
- `GET /api/agents/system/status` - Overall system status

## 🔧 Configuration

### Environment Variables
```bash
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///database/app.db
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
```

### Agent Configuration
Agents can be configured through their respective initialization parameters in `src/agents.py`:
- Triage rules and thresholds
- Communication templates
- Optimization parameters
- Memory retention policies

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python src/tests.py

# Run specific test categories
python -m pytest src/tests.py::TestAgentSystem
python -m pytest src/tests.py::TestDataProcessing
```

### Test Coverage
The system includes comprehensive testing covering:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Edge Case Tests**: Error handling and boundary conditions
- **Performance Tests**: Load testing and scalability validation
- **Memory Tests**: Memory system functionality
- **API Tests**: Endpoint validation

## 📈 Performance & Scalability

The system is designed to handle:
- **10x load increase** through horizontal scaling
- **Sub-second response times** for API endpoints
- **Concurrent agent operations** with proper resource management
- **Memory optimization** with automatic cleanup and capacity limits
- **Database optimization** with proper indexing and query optimization

## 🔒 Security

Security features include:
- **JWT-based authentication** with role-based access control
- **Password hashing** with bcrypt
- **CORS configuration** for cross-origin requests
- **Input validation** and sanitization
- **Rate limiting** on API endpoints
- **HTTPS support** in production (Nginx configuration provided)

## 📚 Documentation

### Architecture & Implementation
- **`BACKEND_OVERVIEW.md`** - Detailed backend implementation, data pipelines, MCP server, agent orchestration
- **`SYSTEM_ARCHITECTURE.md`** - System architecture, deployment, scaling
- **`QUICK_START.md`** - 5-minute deployment guide
- **`DEPLOYMENT.md`** - Comprehensive deployment instructions

### API Documentation
- RESTful API endpoints with examples
- MCP (Model Context Protocol) server endpoints
- Request/response schemas
- Error code definitions

## 🚀 Deployment

### Development
```bash
python start.py
# or
python src/main.py
```

### Production
The system supports multiple deployment options:
- **Docker containers** with multi-stage builds
- **Docker Compose** for easy orchestration
- **Nginx** reverse proxy with SSL support
- **Monitoring** with Prometheus and Grafana

### Docker Commands
```bash
# Start production stack
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Scale web service
docker compose -f docker-compose.prod.yml up --scale web=3 -d

# Stop services
docker compose -f docker-compose.prod.yml down
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation files
- Review the test suite for usage examples
- Check `QUICK_START.md` for common issues

## 🔄 Version History

- **v1.0.0** - Initial release with full multi-agent system
  - Lead triage, engagement, and optimization agents
  - MCP server implementation (WebSocket + HTTP)
  - Comprehensive memory system (4-layer architecture)
  - Production-ready API endpoints
  - Full test suite with edge case handling
  - Docker deployment with monitoring stack
  - Comprehensive documentation

---

**Built with ❤️ for scalable marketing automation**

