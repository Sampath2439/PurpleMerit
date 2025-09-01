@echo off
REM Multi-Agent Marketing System - Windows Deployment Script

setlocal enabledelayedexpansion

REM Colors (Windows doesn't support colors in batch, but we can use echo)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

echo ==========================================
echo Multi-Agent Marketing System Deployment
echo ==========================================
echo.

REM Check if Docker is installed
echo %INFO% Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo %SUCCESS% All prerequisites are met.

REM Setup environment
echo %INFO% Setting up environment...
if not exist .env (
    if exist env.template (
        echo %INFO% Creating .env file from template...
        copy env.template .env >nul
        echo %WARNING% Please update the .env file with your actual configuration values.
    ) else (
        echo %ERROR% No environment template found. Please create a .env file.
        exit /b 1
    )
) else (
    echo %SUCCESS% Environment file already exists.
)

REM Build and start services
echo %INFO% Building and starting services...
docker-compose -f docker-compose.prod.yml down >nul 2>&1
docker-compose -f docker-compose.prod.yml up --build -d

if errorlevel 1 (
    echo %ERROR% Failed to start services.
    exit /b 1
)

echo %SUCCESS% Services started successfully.

REM Wait for services to be ready
echo %INFO% Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Test health endpoint
echo %INFO% Testing health endpoint...
for /l %%i in (1,1,30) do (
    curl -f http://localhost:5000/health >nul 2>&1
    if not errorlevel 1 (
        echo %SUCCESS% Web service is ready.
        goto :health_ok
    )
    timeout /t 2 /nobreak >nul
)

echo %ERROR% Web service failed to start within 60 seconds.
exit /b 1

:health_ok

REM Run database migrations
echo %INFO% Running database migrations...
docker-compose -f docker-compose.prod.yml exec -T web python -c "import sys; sys.path.insert(0, 'src'); from main import app, db; app.app_context().push(); db.create_all(); print('Database tables created successfully.')"

if errorlevel 1 (
    echo %WARNING% Database migration failed, but continuing...
) else (
    echo %SUCCESS% Database migrations completed.
)

REM Run tests
echo %INFO% Running system tests...

curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Health endpoint test failed.
    exit /b 1
)
echo %SUCCESS% Health endpoint test passed.

curl -f http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo %ERROR% API health endpoint test failed.
    exit /b 1
)
echo %SUCCESS% API health endpoint test passed.

curl -f http://localhost:5000/api/agents/health >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Agents health endpoint test failed.
    exit /b 1
)
echo %SUCCESS% Agents health endpoint test passed.

echo %SUCCESS% All tests passed.

REM Show deployment status
echo.
echo %INFO% Deployment Status:
echo.

docker-compose -f docker-compose.prod.yml ps

echo.
echo %INFO% Service URLs:
echo   - Web Application: http://localhost:5000
echo   - API Health Check: http://localhost:5000/health
echo   - Grafana Dashboard: http://localhost:3000 (admin/admin)
echo   - Prometheus: http://localhost:9090
echo   - Neo4j Browser: http://localhost:7474

echo.
echo %INFO% Useful Commands:
echo   - View logs: docker-compose -f docker-compose.prod.yml logs -f
echo   - Stop services: docker-compose -f docker-compose.prod.yml down
echo   - Restart services: docker-compose -f docker-compose.prod.yml restart
echo   - Scale web service: docker-compose -f docker-compose.prod.yml up --scale web=3 -d

echo.
echo %SUCCESS% Deployment completed successfully!
echo %INFO% The system is now running and ready to use.

pause
