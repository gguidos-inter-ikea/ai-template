# Architecture Overview

This document provides an overview of the architecture of the FastAPI Microservice Boilerplate.

## Architectural Principles

The architecture follows these key principles:

1. **Clean Architecture**: Separation of concerns with clear boundaries between layers
2. **Domain-Driven Design**: Business logic organized around domains
3. **Dependency Injection**: Inversion of control for better testability and maintainability
4. **SOLID Principles**: Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion

## Layers

The application is organized into the following layers:

### 1. Infrastructure Layer (`src/base/infrastructure/`)

The infrastructure layer contains implementations of external services and technologies:

- **MongoDB Client**: Handles database connections and operations
- **Redis Client**: Provides caching and rate limiting functionality

### 2. Repository Layer (`src/domains/*/repositories/`)

The repository layer abstracts data access:

- Provides domain-specific data access methods
- Hides the details of the underlying data storage
- Translates between domain entities and database models

### 3. Service Layer (`src/domains/*/services/`)

The service layer contains business logic:

- Implements domain-specific business rules
- Orchestrates operations across multiple repositories
- Handles caching and other cross-cutting concerns

### 4. Interface Layer (`src/domains/*/interfaces/`, `src/base/interfaces/`)

The interface layer exposes the application to the outside world:

- API endpoints defined using FastAPI routers
- Request validation using Pydantic models
- Response formatting and error handling

### 5. System Layer (`src/base/system/`)

The system layer provides application-wide functionality:

- Rate limiting configuration
- Route registration
- Middleware registration

## Dependency Injection

The application uses the `dependency-injector` package to manage dependencies:

- **Base Container** (`src/base/dependencies/di_container.py`): Provides infrastructure components
- **Domain Containers** (`src/domains/*/di_container.py`): Extend the base container with domain-specific components

## Application Lifecycle

The application lifecycle is managed through the lifespan context manager:

- **Startup**: Connect to databases, initialize rate limiters
- **Shutdown**: Close connections, clean up resources

## Request Flow

1. **Request Received**: FastAPI receives an HTTP request
2. **Middleware Processing**: Request passes through middleware (logging, security headers, etc.)
3. **Route Matching**: FastAPI matches the request to a route
4. **Dependency Resolution**: Dependencies are resolved (including rate limiters)
5. **Request Validation**: Request data is validated using Pydantic models
6. **Handler Execution**: Route handler is executed, calling service methods
7. **Response Generation**: Response is generated and returned
8. **Middleware Post-Processing**: Response passes through middleware
9. **Response Sent**: HTTP response is sent to the client

## Domain Extension

The architecture is designed to be easily extensible with new domains:

1. Create a new domain directory in `src/domains/`
2. Implement repositories, services, and interfaces
3. Create a domain-specific container that extends the base container
4. Register the domain container in `src/domains/__init__.py`
5. Register domain routes in `src/domains/routes.py`

## Monitoring and Observability

The application includes monitoring and observability features:

- **Prometheus Metrics**: Exposed at `/internal/metrics`
- **Health Checks**: Available at `/internal/health` and `/internal/readiness`
- **Structured Logging**: JSON-formatted logs with contextual information

## Security

Security features include:

- **Rate Limiting**: Prevents abuse of the API
- **Security Headers**: Middleware adds security-related HTTP headers
- **CORS Configuration**: Controls cross-origin requests
- **API Key Authentication**: Optional API key validation

## Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  Base Interfaces │    │ Domain Interfaces│                 │
│  └────────┬────────┘    └────────┬────────┘                 │
│           │                      │                          │
│  ┌────────▼────────┐    ┌────────▼────────┐                 │
│  │  Base Services  │    │ Domain Services │                 │
│  └────────┬────────┘    └────────┬────────┘                 │
│           │                      │                          │
│           │             ┌────────▼────────┐                 │
│           │             │Domain Repositories                │
│           │             └────────┬────────┘                 │
│           │                      │                          │
│  ┌────────▼────────────────────▼─────────┐                 │
│  │           Infrastructure Layer          │                 │
│  └─────────────────────────────────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
     │                 │                  │
     ▼                 ▼                  ▼
┌─────────┐      ┌─────────┐       ┌──────────┐
│ MongoDB │      │  Redis  │       │ Prometheus│
└─────────┘      └─────────┘       └──────────┘
```

## Further Reading

- [Dependency Injection](dependency_injection.md): Detailed explanation of the DI system
- [Rate Limiting](rate_limiting.md): Rate limiting configuration and usage
- [Adding a New Domain](adding_new_domain.md): Step-by-step guide to adding new domains 