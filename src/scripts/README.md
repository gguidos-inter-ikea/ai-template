# Utility Scripts

This directory contains utility scripts for the application.

## Database Connection Test Script

The `test_db_connection.py` script allows you to test connections to MongoDB and Redis databases without starting the entire application. This is useful for troubleshooting connection issues.

### Usage

```bash
# Test both MongoDB and Redis connections
python -m src.scripts.test_db_connection

# Test only MongoDB connection
python -m src.scripts.test_db_connection --mongodb

# Test only Redis connection
python -m src.scripts.test_db_connection --redis
```

### Common Database Connection Issues

#### MongoDB Connection Issues

1. **Hostname Resolution**:
   - Error: `Name or service not known` or `Could not connect to mongodb:27017`
   - Solution: Check if the hostname is correct in your `.env` file. If using Docker, ensure the service name matches your Docker Compose configuration.

2. **Authentication Issues**:
   - Error: `Authentication failed`
   - Solution: Verify username, password, and authentication database in your connection string.

3. **Network Issues**:
   - Error: `Connection refused`
   - Solution: Ensure MongoDB is running and accessible from your application (check firewalls, Docker network configurations).

#### Redis Connection Issues

1. **Connection Refused**:
   - Error: `Connection refused` or `Could not connect to Redis at redis:6379`
   - Solution: Verify Redis is running and the host/port in your `.env` file are correct.

2. **Authentication Issues**:
   - Error: `NOAUTH Authentication required` or `invalid password`
   - Solution: Check the Redis password in your `.env` file.

3. **DB Index Out of Range**:
   - Error: `DB index is out of range`
   - Solution: Redis typically has 16 databases (0-15). Make sure your `REDIS_DB` setting is within this range.

### Environment Setup

Ensure your `.env` file has the correct database connection information:

```
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DBNAME=your_db_name

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

For Docker environments, your hostnames would typically match your service names, e.g., `mongodb` and `redis`.

### Troubleshooting Docker Setup

If running the application in Docker:

1. Check that the database services are running:
   ```bash
   docker compose ps
   ```

2. Check logs for database services:
   ```bash
   docker compose logs mongodb
   docker compose logs redis
   ```

3. Make sure your application container can connect to the database containers:
   ```bash
   docker compose exec app ping mongodb
   docker compose exec app ping redis
   ```

4. Verify the Docker network setup:
   ```bash
   docker network ls
   docker network inspect <network_name>
   ``` 