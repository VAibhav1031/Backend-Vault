# Task Manager API (Backend Services)....

A fully REST-based API service for task management with authentication, featuring signup, login, and password reset with OTP email verification. Built following RESTful design principles with JWT-secured endpoints and consistent error handling.

## Features:

- **Authentication**: Signup, login, password reset with OTP email verification
- **Task Management**: Full CRUD operations for tasks
- **Security**: JWT token-based authentication, Rate Limitting, Ip-Ban
- **Consistent Error Handling**: Standardized error responses across all endpoints
- **RESTful Design**: Following REST API best practices

## Tech Stack:

- **Backend**: Python, Flask, Marshmallow, JWT, Pytest, uv, Alembic
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Architecture**: Factory method pattern for scalable development, it is good for development and future scaling , if you want to 

## Configuration:

The application uses separate configurations for different environments:

- **DevConfig**: Development mode (default), uses Docker PostgreSQL for persistent testing
- **ProdConfig**: Production deployment configuration  
- **TestConfig**: Unit testing with SQLite in-memory database

Each configuration has its own database settings and feature flags defined in separate blueprint classes.

## Project Structure:

```
__init__.py (main app initialization and object creation)
```

The main application file handles initialization and attaches all components as dynamic attributes to the Flask app object.

## API Routes:

### Authentication::
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User authentication
- `POST /api/auth/forget-password` - Initiate password reset
- `POST /api/auth/verify-otp` - Verify OTP for password reset
- `POST /api/auth/reset-password` - Complete password reset

### Tasks::
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/task-id` - Get specific task
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/task-id` - Update existing task
- `DELETE /api/tasks` - Delete all tasks
- `DELETE /api/tasks/task-id` - Delete specific task

Routes are organized into **AUTH** and **TASKS** modules, each with validation using **Marshmallow** for JSON data validation including size, type, and content constraints.

## Error Handling:

Standardized error response structure used across all endpoints:

```python
def error_response(code, status, message=None, reason=None, details=None):
    return (
        jsonify(
            {
                "errors": {
                    "code": code,
                    "type": code.lower(),
                    "status": status,
                    "message": message or central_registry.get(code, "Unknown error"),
                    "reason": reason,
                    "details": details,
                    "instance": _make_instance(),
                }
            }
        ),
        status,
    )
```

Supported error types/used in this project : internal_server_error, not_found, bad_request, unauthorized_error, too_many_requests, forbidden_access

## Logging:

Custom logging configuration using Python's logging library with dictConfig:
- Stream and file logging support
- Scalable to external services (ELK stack)
- Root logging structure with module-level propagation

## Database Migration:

- **Development**: Managed by Alembic through Docker scripts
- **Testing**: Uses SQLite in-memory (no migration needed)
- **Production**: Alembic migration management

## Usage:

### Quick Start::

```bash
# Start the application
docker compose up

# Stop the application  
docker compose down

# Remove volumes (clean reset)
docker compose down -v
```

### Development with Live Reload

```bash
# Start with file watching for development
docker compose up --watch
```

Ensure your compose file includes the `develop` section:

```yaml
develop:
  watch:
    - action: rebuild
      path: . # . means your current working directory cause your compose file is in the project dir brother
      target: /task_app # your application folder in the container
      ignore: # even if you use the .dockerignore , it is best practice for protection
        - .venv/
        - .git/
        - __pycache__/
        - "*.egg-info/"
```

## Environment Setup

The application automatically uses development mode by default. For production deployment, set the appropriate environment variables for your domain and database configuration.
