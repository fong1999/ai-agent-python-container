# Bedrock API Bridge

A secure API bridge between frontend applications and AWS Bedrock AI models, built with FastAPI and designed for containerized deployment.

## Features

- REST API interface with OpenAI-compatible endpoints
- Secure authentication with API keys
- Support for multiple AWS Bedrock models (Claude, Llama, etc.)
- Chat completions and text completions endpoints
- Streaming support for real-time responses
- Usage tracking and monitoring
- Comprehensive logging
- Health check endpoints
- Designed for containerized deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- AWS credentials with access to Bedrock
- Python 3.9+ (for local development)

### File Structure

# Project Structure for Bedrock API Bridge

```
bedrock-api-bridge/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── completions.py
│   │   │   ├── health.py
│   │   │   └── models.py
│   │   └── router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── completions.py
│   │   └── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bedrock.py
│   │   └── usage_tracking.py
│   └── utils/
│       ├── __init__.py
│       └── token_helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_chat.py
│   │   └── test_health.py
│   └── test_services/
│       ├── __init__.py
│       └── test_bedrock.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── Makefile
├── README.md
├── deployment/
│   ├── harness/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── k8s/
│       ├── deployment.yaml
│       └── service.yaml
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

### Key Files

Core Application Files:

* app/main.py - The FastAPI application entry point
* app/core/config.py - Configuration settings
* app/api/endpoints/*.py - API endpoint handlers for chat, completions, etc.
* app/services/bedrock.py - Service for interacting with AWS Bedrock


Deployment Files:

* Dockerfile - Containerizes the application
* .github/workflows/ci-cd.yml - GitHub Actions for CI
* iac/*.yaml - Kubernetes deployment manifests

### Running Locally with Docker

1. Clone the repository:
   ```bash
   git clone this repo
   cd <project_name>
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

3. Start the service with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. The API will be available at http://localhost:8000

### Local Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, access the OpenAPI documentation at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Key Endpoints

- **GET /health**: Health check endpoint
- **GET /v1/models**: List available models
- **POST /v1/chat/completions**: Chat completion endpoint
- **POST /v1/completions**: Text completion endpoint

## Authentication

All API endpoints (except `/health`) require API key authentication using the `X-API-Key` header.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated list of valid API keys | None (Required) |
| `AWS_REGION` | AWS region for Bedrock | us-east-1 |
| `LOG_LEVEL` | Logging level | INFO |
| `CORS_ORIGINS` | Allowed CORS origins | * |
| `AWS_ACCESS_KEY_ID` | AWS access key (if not using IAM roles) | None |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (if not using IAM roles) | None |

## Deployment

### Kubernetes Deployment

Kubernetes deployment manifests are provided in the `deployment/k8s/` directory.

```bash
kubectl apply -f iac/deployment.yaml
kubectl apply -f iac/service.yaml
```

## CI Pipeline

This project includes GitHub Actions workflows for:
- Running tests
- Building and pushing Docker images
- Deploying to dev/test/prod environments

## Usage Examples

### Chat Completion

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "model": "anthropic.claude-3-sonnet-20240229-v1:0",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Write a haiku about clouds."}
    ],
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

Please do not store API keys in your code or commit them to version control. Use environment variables or a secrets management system.

## Additional Considerations

* AWS IAM Roles: In production, use IAM roles instead of access keys
* Monitoring: Consider adding Prometheus metrics
* Testing: Implement comprehensive tests (a tests directory is included)
* Load Testing: Verify performance under load before production deployment

This containerized approach gives us:

* Scalability through Kubernetes
* Maintainability through clean architecture
* Security through proper containerization
* CI/CD automation for reliable deployments