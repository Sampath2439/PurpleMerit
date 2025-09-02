# Database Setup Guide

This guide will help you connect your own database to the Multi-Agent Marketing System.

## Quick Start

### Option 1: Use the Setup Script (Recommended)
```bash
python setup_database.py
```

### Option 2: Use Docker Compose
```bash
# Start PostgreSQL + Redis
docker-compose -f docker-compose.db.yml up -d

# Or start MySQL + Redis
docker-compose -f docker-compose.db.yml --profile mysql up -d

# Access pgAdmin (PostgreSQL admin interface)
docker-compose -f docker-compose.db.yml --profile admin up -d
```

## Database Options

### 1. PostgreSQL (Recommended for Production)

**Connection String Format:**
```
postgresql://username:password@host:port/database_name
```

**Example:**
```bash
export DATABASE_URL="postgresql://marketing_user:password123@localhost:5432/marketing_system"
```

**Docker Setup:**
```bash
docker run --name marketing_postgres \
  -e POSTGRES_DB=marketing_system \
  -e POSTGRES_USER=marketing_user \
  -e POSTGRES_PASSWORD=password123 \
  -p 5432:5432 \
  -d postgres:15-alpine
```

### 2. MySQL

**Connection String Format:**
```
mysql+pymysql://username:password@host:port/database_name
```

**Example:**
```bash
export DATABASE_URL="mysql+pymysql://marketing_user:password123@localhost:3306/marketing_system"
```

**Docker Setup:**
```bash
docker run --name marketing_mysql \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=marketing_system \
  -e MYSQL_USER=marketing_user \
  -e MYSQL_PASSWORD=password123 \
  -p 3306:3306 \
  -d mysql:8.0
```

### 3. SQLite (Development Only)

**Connection String Format:**
```
sqlite:///path/to/database.db
```

**Example:**
```bash
export DATABASE_URL="sqlite:///./database/app.db"
```

## Environment Configuration

### Create a .env file:
```bash
# Database Configuration
DATABASE_URL=postgresql://marketing_user:password123@localhost:5432/marketing_system

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key

# Agent Configuration
MAX_CONCURRENT_AGENTS=10
AGENT_TIMEOUT_SECONDS=300

# Memory Configuration
MAX_MEMORY_ENTRIES=10000
MEMORY_CLEANUP_INTERVAL=3600

# MCP Server Configuration
MCP_HOST=localhost
MCP_PORT=8080

# Security Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
```

## Cloud Database Options

### AWS RDS
```bash
export DATABASE_URL="postgresql://username:password@your-rds-endpoint:5432/marketing_system"
```

### Google Cloud SQL
```bash
export DATABASE_URL="postgresql://username:password@/marketing_system?host=/cloudsql/project:region:instance"
```

### Azure Database
```bash
export DATABASE_URL="postgresql://username:password@your-server.postgres.database.azure.com:5432/marketing_system"
```

## Testing Your Connection

1. **Set your environment variable:**
   ```bash
   export DATABASE_URL="your_connection_string_here"
   ```

2. **Test the connection:**
   ```bash
   python setup_database.py
   # Choose option 4 to test existing connection
   ```

3. **Start the application:**
   ```bash
   python start.py
   ```

## Troubleshooting

### Common Issues:

1. **Connection Refused:**
   - Check if the database server is running
   - Verify the host and port
   - Check firewall settings

2. **Authentication Failed:**
   - Verify username and password
   - Check if the user has proper permissions

3. **Database Not Found:**
   - Create the database manually
   - Check database name spelling

4. **Permission Denied:**
   - Grant proper permissions to the user
   - Check database user roles

### Useful Commands:

**PostgreSQL:**
```bash
# Connect to database
psql -h localhost -U marketing_user -d marketing_system

# List databases
\l

# List tables
\dt
```

**MySQL:**
```bash
# Connect to database
mysql -h localhost -u marketing_user -p marketing_system

# List databases
SHOW DATABASES;

# List tables
SHOW TABLES;
```

## Production Considerations

1. **Use connection pooling** for better performance
2. **Enable SSL** for secure connections
3. **Set up regular backups**
4. **Monitor database performance**
5. **Use read replicas** for scaling

## Next Steps

After setting up your database:

1. Run the application: `python start.py`
2. The system will automatically create all required tables
3. Access the web interface at `http://localhost:5000`
4. Test the API endpoints at `http://localhost:5000/api`

## Support

If you encounter any issues:
1. Check the application logs
2. Verify your database connection
3. Ensure all required packages are installed
4. Check the troubleshooting section above
