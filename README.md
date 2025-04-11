# FastAPI Microservice Boilerplate

A robust, production-ready boilerplate for building FastAPI microservices with best practices.

## Features

- **Modern FastAPI Framework**: Built on FastAPI for high performance and easy development
- **Clean Architecture**: Follows domain-driven design principles with clear separation of concerns
- **Dependency Injection**: Uses `dependency-injector` for clean, testable, and maintainable code
- **Database Integration**: MongoDB support with async drivers
- **Caching**: Redis integration for caching and rate limiting
- **Rate Limiting**: Configurable rate limiting with multiple strategies
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Containerization**: Docker and Docker Compose setup for easy deployment
- **Extensible**: Easy to add new domains without modifying the base code
- **Documentation**: Auto-generated API documentation with Swagger UI
- **Logging**: Structured logging with different levels and outputs
- **Health Checks**: Ready-to-use health check endpoints
- **Security**: Built-in security headers and CORS configuration
- **Error Handling**: Comprehensive domain-specific exception handling system
- **Troubleshooting**: Built-in tools for diagnosing and resolving connection issues
- **Security Monitoring**: Real-time monitoring of security events with alerts and log rotation

## Project Structure

```
python-new-bp/
├── docs/                      # Documentation files
├── src/                       # Source code
│   ├── base/                  # Base infrastructure code
│   │   ├── config/            # Configuration settings
│   │   ├── dependencies/      # Dependency injection container
│   │   ├── handlers/          # Global exception handlers
│   │   ├── infrastructure/    # Infrastructure implementations (MongoDB, Redis)
│   │   │   └── exceptions.py  # Infrastructure-specific exceptions
│   │   ├── interfaces/        # API interfaces for base functionality
│   │   ├── lifespan/          # Application lifecycle management
│   │   ├── middlewares/       # Middleware components
│   │   ├── scripts/           # Utility scripts
│   │   │   ├── security_monitor.py  # Security monitoring system
│   │   │   ├── SECURITY_MONITOR.md  # Security monitor documentation
│   │   │   └── test_db_connection.py # Test database connections
│   │   └── system/            # System-level components
│   ├── domains/               # Business domains
│   │   └── example/           # Example domain implementation
│   │       ├── di_container.py # Domain-specific DI container
│   │       ├── interfaces/    # API interfaces for the domain
│   │       ├── repositories/  # Data access layer
│   │       └── services/      # Business logic
│   ├── scripts/               # Utility scripts
│   │   ├── test_db_connection.py # Test database connections
│   │   └── fix_docker_networking.sh # Fix Docker networking issues
│   └── main.py                # Application entry point
├── .env                       # Environment variables for local development
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── prometheus.yml             # Prometheus configuration
└── requirements.txt           # Python dependencies
```

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended for containerized deployment)
- Python 3.9+ (for local development)
- MongoDB
- Redis

### Running with Docker (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/yourusername/python-new-bp.git
cd python-new-bp
```

2. Create a `.env` file for Docker Compose:

```bash
cp .env.example .env
# Edit the .env file with your configuration
```

3. Build and run the containers:

```bash
docker-compose up --build
```

4. Access the API documentation at http://localhost:8000/docs

The Docker Compose setup includes:
- The API service
- MongoDB database
- Redis for caching and rate limiting
- Prometheus for metrics collection
- Grafana for metrics visualization

### Local Development

If you prefer to run the application locally during development:

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file for local development:

```bash
cp .env.example .env
# Edit the .env file with your configuration
# Make sure to set REDIS_HOST and MONGODB_URI to point to your local or remote instances
```

3. Run the application:

```bash
uvicorn src.main:app --reload
```

Note: When running locally, you'll need to have MongoDB and Redis instances available. You can either:
- Use Docker to run just the database services: `docker-compose up mongo redis`
- Install MongoDB and Redis locally
- Use remote instances (update your .env file accordingly)

## Configuration

The application is configured using environment variables that can be set in the `.env` file for both Docker Compose and local development.

Key configuration options:

- `PROJECT_NAME`: Name of the project
- `ENVIRONMENT`: Development, staging, or production
- `API_KEY`: API key for authentication
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DBNAME`: MongoDB database name
- `REDIS_HOST`: Redis host (use "redis" for Docker, "localhost" for local dev)
- `REDIS_PORT`: Redis port
- `PORT`: Port to run the application on

### Docker vs Local Environment Variables

When running with Docker Compose, the environment variables from your `.env` file are passed to the containers automatically as defined in the `docker-compose.yml` file. For certain variables like `REDIS_HOST`, the Docker Compose setup uses internal Docker networking (e.g., `REDIS_HOST=redis` to connect to the Redis container).

For local development, you'll need to adjust these variables to point to your local services (e.g., `REDIS_HOST=localhost`).

## Troubleshooting Database Connection Issues

If you encounter database connection issues, the application includes several tools to help diagnose and fix the problems:

### Testing Database Connections

Use the included test script to verify database connections:

```bash
# Testing both MongoDB and Redis connections
python -m src.scripts.test_db_connection

# Testing only MongoDB connection
python -m src.scripts.test_db_connection --mongodb

# Testing only Redis connection
python -m src.scripts.test_db_connection --redis
```

When running in Docker, you can execute the test within the container:

```bash
docker compose exec app python -m src.scripts.test_db_connection
```

### Fixing Docker Networking Issues

If you're using Docker and experiencing connection issues between services, use the provided fix script:

```bash
# Make the script executable if needed
chmod +x src/scripts/fix_docker_networking.sh

# Run the script
./src/scripts/fix_docker_networking.sh
```

This script helps resolve common issues such as:
- Incorrect hostnames in connection strings
- Redis database index out of range
- Network connectivity between containers
- Missing or misconfigured environment variables

For more troubleshooting information, see [src/scripts/README.md](src/scripts/README.md).

## Error Handling System

The application includes a comprehensive error handling system with:

- **Domain-Specific Exceptions**: Custom exception classes for each domain (e.g., `UserNotFoundError`)
- **Infrastructure Exceptions**: Specialized exceptions for database connectivity issues
- **Global Exception Handlers**: Properly formatted API responses for different error types
- **Structured Error Responses**: Consistent JSON format for all API errors

Error responses include:
- HTTP status code
- Error message
- Error code (for domain-specific errors)
- Additional context for debugging (in development mode)

## Documentation

- [API Documentation](http://localhost:8000/docs) - Swagger UI for API endpoints
- [Architecture](docs/architecture.md) - Overview of the system architecture
- [Rate Limiting](docs/rate_limiting.md) - Details on rate limiting implementation
- [Dependency Injection](docs/dependency_injection.md) - How DI is used in the project
- [Monitoring](docs/monitoring.md) - Prometheus and Grafana integration
- [Exception Handling](docs/exception_handling.md) - Global exception handling system
- [Adding a New Domain](docs/adding_new_domain.md) - How to add a new domain to the API
- [Security Features](docs/security.md) - Authentication, authorization and security features
- [Repository Pattern](docs/repository_pattern.md) - Data access abstraction patterns
- [Session Tracking](docs/session_tracking.md) - Request/response tracking and analytics

## Adding a New Domain

The boilerplate is designed to make it easy to add new domains without modifying the base code. See [Adding a New Domain](docs/adding_new_domain.md) for a detailed guide.

## Monitoring

The application includes Prometheus metrics and Grafana dashboards for monitoring. Access Prometheus at http://localhost:9090 and Grafana at http://localhost:3000 when running with Docker Compose.

## Security Features

The application includes comprehensive security features:

### Authentication and Authorization
- JWT-based authentication
- Role-based access control
- API key management
- IP filtering for protected endpoints

### Security Headers and Protection
- Strict security headers (HSTS, CSP, etc.)
- CORS configuration
- Input validation
- Rate limiting

### Security Monitoring and Alerts
- Real-time security event monitoring and analysis
- Pattern-based attack detection
- Historical event analysis
- Rich HTML and plain text email alerts
- Configurable alert thresholds and cooldowns
- Comprehensive security metrics
- Integration with Prometheus and Grafana
- IP-based threat detection
- Rate limit violation tracking

### Logging and Auditing
- Structured JSON logging
- Automatic log rotation and management
- Security event correlation
- Request/response tracking
- Performance metrics collection

For detailed security documentation, see:
- [Security Features](docs/security.md)
- [Security Monitor](src/base/scripts/SECURITY_MONITOR.md)
- [Monitoring](docs/monitoring.md)
- [Logging](docs/logging.md)

## Security and Error Monitoring

### Security Monitor

The application includes a real-time security monitoring system that monitors logs for security events, 
rate limiting violations, and application errors. It processes these events and sends alerts when 
suspicious activity or critical errors are detected.

#### Configuration

Security and error monitoring can be configured in `src/base/config/config.py`:

- `enabled_log_types`: List of log types to monitor (`security`, `rate_limit`, `error`)
- `alert_cooldown_minutes`: Minutes to wait between alerts
- `unauthorized_access_threshold`: Number of unauthorized attempts before alerting
- `rate_limit_threshold`: Number of rate limit violations before alerting
- `error_threshold`: Number of errors before triggering an alert
- `error_time_window_minutes`: Time window for counting errors
- `error_log_path`: Path to the error log file

#### Error Monitoring

The application includes a dedicated error monitoring system that:

1. Scans error logs for application errors
2. Counts errors by module and type
3. Sends alerts when error thresholds are exceeded

**Components:**

- `src/base/scripts/error_monitor.py`: Main error monitoring class
- `src/base/scripts/run_error_monitor.py`: Script to run the monitor as a service
- `src/base/scripts/test_error_monitor.py`: Script to test the monitor
- `src/base/scripts/add_test_error.py`: Utility to add test errors for monitoring

**Running the Error Monitor:**

```bash
# Run the error monitor as a service
python src/base/scripts/run_error_monitor.py

# Test the error monitor once
python src/base/scripts/test_error_monitor.py

# Add a test error for monitoring
python src/base/scripts/add_test_error.py --message "Database connection failed" --module "database"
```

When the error threshold is exceeded, the monitor will log detailed information about the errors
and can be configured to send email alerts.

### Email Alerts

The monitoring system can send email alerts when suspicious activity or critical errors are detected.
Email settings can be configured in `src/base/config/config.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 