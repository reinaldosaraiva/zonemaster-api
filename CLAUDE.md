# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based DNS health check service called "zonemaster-api" built with Python 3.13+. The project uses UV for dependency management and follows a clean architecture pattern with separation of concerns.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Development Server
```bash
# Run development server with hot reload
uv run uvicorn app.main:app --reload

# Run with Docker
docker-compose up
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_main.py::test_root
```

### Code Quality
```bash
# Format code with Ruff
uv run ruff format

# Lint code with Ruff
uv run ruff check

# Fix linting issues automatically
uv run ruff check --fix

# Type checking with MyPy
uv run mypy app/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Database Operations
```bash
# Generate new migration
uv run alembic revision --autogenerate -m "migration message"

# Apply migrations
uv run alembic upgrade head

# Downgrade migration
uv run alembic downgrade -1
```

## DNS Health Check Service Architecture

### Project Structure
```
app/
├── main.py              # FastAPI application entry point
├── core/
│   └── config.py        # Application settings and Zonemaster API config
├── db/
│   ├── base.py          # SQLAlchemy Base class
│   └── session.py       # Async database session configuration
├── models/
│   ├── dns_check.py     # DNSCheck database model
│   └── dns_result.py    # DNSResult database model  
├── schemas/
│   └── dns_check.py     # Pydantic schemas for DNS operations
├── crud/
│   ├── dns_check.py     # DNSCheck CRUD operations
│   └── dns_result.py    # DNSResult CRUD operations
├── services/
│   └── zonemaster_service.py  # Zonemaster API integration
└── api/
    ├── health.py        # Health check endpoint
    └── v1/
        ├── api.py       # Main API router
        └── endpoints/
            └── dns_check.py  # DNS check endpoints
```

### Core Features
**DNS Health Checking:**
- Integrates with Zonemaster Backend API via JSON-RPC 2.0
- Performs asynchronous DNS analysis for domains
- Stores results in PostgreSQL database for historical tracking
- Provides REST API for creating checks and retrieving results

**Database Models:**
- `DNSCheck`: Stores domain and creation timestamp
- `DNSResult`: Stores individual test results (level, module, tag, message)
- One-to-many relationship between checks and results

**API Endpoints:**
- `POST /api/v1/checks/` - Create new DNS check
- `GET /api/v1/checks/{id}` - Get specific check with results  
- `GET /api/v1/checks/` - List checks with pagination and result counts

### Configuration
- **Database**: PostgreSQL with async support (asyncpg driver)
- **Zonemaster Integration**: HTTP client calls to JSON-RPC API
- **Environment Variables**: Database URLs, Zonemaster API URL, timeouts
- **Settings**: Managed via Pydantic Settings with `.env` support

### Dependencies
**Core:**
- FastAPI for web framework
- SQLAlchemy 2.0 with asyncio support
- AsyncPG for PostgreSQL async driver
- HTTPX for Zonemaster API calls
- Alembic for database migrations

**Development:**
- Pytest with async support and HTTPX mocking
- Ruff for linting and formatting
- MyPy for type checking

### Zonemaster Integration
**API Communication:**
- Uses JSON-RPC 2.0 protocol
- Calls `start_domain_test` method with domain and profile
- Handles API errors and connection failures gracefully
- Parses response and stores structured results

**Error Handling:**
- Connection timeouts (5 minutes default)
- API error responses mapped to HTTP 503
- Robust error propagation with meaningful messages

## Development Notes

### Testing Strategy
**Comprehensive Test Coverage:**
- Async test setup with in-memory SQLite
- Zonemaster API mocking using pytest-httpx
- Tests cover success, error, and unavailable scenarios
- Database cleanup between tests
- Pagination and validation testing

### Docker Environment
**Complete Stack:**
- PostgreSQL 15 database with health checks
- Zonemaster Backend service
- FastAPI application with auto-migrations
- Volume mounting for development
- Service dependencies and health monitoring

### Migration Management
- Alembic configured for PostgreSQL
- Separate sync/async database URL configuration
- Automatic migration execution on container startup
- Manual migration created for DNS tables