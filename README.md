# FastAPI + PostgreSQL + AWS Cognito + Floci Demo

A FastAPI backend demonstrating PostgreSQL, SQLAlchemy 2.0 async, AWS Cognito authentication, Celery workers, and Floci for local AWS service emulation.

## Architecture

```
                      Developer
                          |
                          v
                       Nginx
                          |
                          v
                      FastAPI
                       /    \
                      /      \
                     v        v
                PostgreSQL   Redis
                  Docker     Docker
                             |
                             v
                          Celery
                          Worker
                             |
                             v
                           Floci
                             |
           +-----------------+----------------+
           |                 |                |
           v                 v                v
          S3             Cognito         EventBridge
       (Floci)           (Floci)           (Floci)
```

## Prerequisites

- Docker & Docker Compose
- Python 3.13+ (for local development outside Docker)

## Project Structure

```
app/
  main.py                        # FastAPI application
  core/
    config.py                    # Settings
    database.py                  # SQLAlchemy async engine
    security.py                  # JWT validation
    redis.py                     # Redis client
    logging.py                   # Logging configuration
    exceptions.py                # API exceptions
  integrations/
    aws/
      clients.py                 # AWS client factory
  models/
    user.py                      # User model
    item.py                      # Item model
  schemas/
    auth.py                      # Auth schemas
    user.py                      # User schemas
    item.py                      # Item schemas
  repositories/
    user.py                      # User database ops
    item.py                      # Item database ops
  services/
    cognito.py                   # Cognito service
    auth.py                      # Auth service
    item.py                      # Item service
    aws/
      s3.py                      # S3 service
      eventbridge.py             # EventBridge service
  tasks/
    __init__.py
    email.py                     # Email tasks
    notifications.py             # Notification tasks
    cleanup.py                   # Cleanup tasks
  worker/
    celery_app.py                # Celery configuration
  api/
    deps.py                      # FastAPI dependencies
    routes/
      auth.py                    # Auth endpoints
      users.py                   # User endpoints
      items.py                   # Item endpoints
alembic/
  env.py                         # Alembic async config
tests/
  conftest.py                    # Test fixtures
  test_auth.py                   # Auth tests
  test_users.py                  # User tests
  test_items.py                  # Item tests
nginx/
  nginx.dev.conf                 # Nginx config
terraform/
  modules/
    vpc/                         # VPC module
    ecr/                         # ECR module
    alb/                         # ALB module
    ecs/                         # ECS module
    rds/                         # RDS module
    redis/                       # ElastiCache module
    cognito/                     # Cognito module
    s3/                          # S3 module
    eventbridge/                 # EventBridge module
    iam/                         # IAM module
    secrets/                     # Secrets Manager module
    cloudwatch/                  # CloudWatch module
  environments/
    dev/                         # Dev environment
```

## Environment Variables

### Development (.env.dev)

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/demo_db
REDIS_URL=redis://redis:6379/0
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_ENDPOINT_URL=http://floci:4566
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
COGNITO_CLIENT_SECRET=
JWT_ISSUER=
JWT_AUDIENCE=
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
S3_BUCKET_NAME=demo-bucket
```

**Never commit real secrets to version control.**

## Quick Start

```bash
# 1. Copy environment variables
cp .env.dev.example .env

# 2. Start all services
docker compose -f docker-compose.dev.yml up -d --build

# 3. Run migrations
docker compose -f docker-compose.dev.yml exec api alembic upgrade head

# 4. Open API docs
open http://localhost:80/docs
```

## Commands

```bash
make up                    # Start dev environment
make down                  # Stop dev environment
make logs                  # Tail API logs
make shell                 # Bash into API container
make migrate               # Apply migrations
make migration name=foo    # Create new migration
make test                  # Run tests
make worker-logs           # Tail Celery worker logs
make beat-logs             # Tail Celery beat logs
make floci-logs            # Tail Floci logs
```

## Terraform

Terraform provisions AWS infrastructure using a modular structure.

### Terraform Commands

```bash
# Initialize Terraform
terraform -chdir=terraform/environments/dev init

# Validate configuration
terraform -chdir=terraform/environments/dev validate

# Plan changes
terraform -chdir=terraform/environments/dev plan -out=tfplan

# Apply changes
terraform -chdir=terraform/environments/dev apply tfplan
```

### AWS Authentication

Terraform uses the standard AWS credential chain:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. Shared credentials file (`~/.aws/credentials`)
3. IAM role (when running on EC2/ECS)

## API Endpoints

### Authentication

| Method | Endpoint               | Auth | Description          |
|--------|------------------------|------|----------------------|
| POST   | /api/v1/auth/register  | No   | Register user        |
| POST   | /api/v1/auth/confirm   | No   | Confirm email        |
| POST   | /api/v1/auth/login     | No   | Login                |
| POST   | /api/v1/auth/refresh   | No   | Refresh token        |
| POST   | /api/v1/auth/logout    | Yes  | Logout               |
| GET    | /api/v1/auth/me        | Yes  | Current user info    |
| GET    | /api/v1/auth/providers | No   | List SSO providers   |
| GET    | /api/v1/auth/{provider}/authorize | No | Initiate SSO |
| GET    | /api/v1/auth/{provider}/callback | No | SSO callback |
| GET    | /api/v1/auth/me/identities | Yes | Linked identities |

### Users

| Method | Endpoint               | Auth | Description          |
|--------|------------------------|------|----------------------|
| GET    | /api/v1/users/me       | Yes  | Current user         |
| GET    | /api/v1/users/me/items | Yes  | Current user items   |

### Items

| Method | Endpoint               | Auth | Description          |
|--------|------------------------|------|----------------------|
| POST   | /api/v1/items          | Yes  | Create item          |
| GET    | /api/v1/items          | Yes  | List own items       |
| GET    | /api/v1/items/{id}     | Yes  | Get item             |
| PATCH  | /api/v1/items/{id}     | Yes  | Update item          |
| DELETE | /api/v1/items/{id}     | Yes  | Delete item          |

## Health Checks

- `GET /health` - Application health
- `GET /health/db` - PostgreSQL connectivity
- `GET /health/redis` - Redis connectivity
- `GET /health/aws` - AWS/Floci connectivity

## SSO Authentication

### Architecture

```
Google ──────┐
             │
Apple ───────┤
             ▼
        AWS Cognito
        User Pool
             │
             ▼
       Cognito JWT
             │
             ▼
          FastAPI
             │
             ▼
      Application User
```

The application uses AWS Cognito as the central identity provider. Google and Apple authenticate through Cognito federation. FastAPI validates Cognito-issued JWTs and resolves local application users.

### Supported Providers

| Provider | Status | Description |
|----------|--------|-------------|
| Google | Optional | Configure via `GOOGLE_SSO_ENABLED=true` |
| Apple | Optional | Configure via `APPLE_SSO_ENABLED=true` |

Additional providers can be added by extending `OAuthService` without modifying business logic.

### Configuration

```env
# Google SSO
GOOGLE_SSO_ENABLED=true
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Apple SSO
APPLE_SSO_ENABLED=true
APPLE_CLIENT_ID=
APPLE_TEAM_ID=
APPLE_KEY_ID=
APPLE_PRIVATE_KEY=
```

### User Identity Model

The `user_identities` table links application users to external identity providers:

```text
User
 |
 +---- UserIdentity (provider=google, provider_subject=...)
 |
 +---- UserIdentity (provider=apple, provider_subject=...)
```

Each `UserIdentity` has a unique constraint on `(provider, provider_subject)`.

### OAuth Flow

1. Client requests authorization URL: `GET /api/v1/auth/{provider}/authorize?redirect_uri=...`
2. Client redirects user to provider authorization URL
3. Provider redirects back to `GET /api/v1/auth/{provider}/callback?code=...&state=...`
4. Application exchanges code for tokens via Cognito
5. Application validates JWT and provisions/links user identity
6. Client receives access token and refresh token

### Security

- OAuth `state` parameter prevents CSRF
- `nonce` parameter prevents replay attacks
- `redirect_uri` is validated against stored state
- JWT validation includes signature, issuer, audience, expiration, and token type checks
- Account linking requires existing authenticated session
- Duplicate external identities are rejected

### Account Linking

Users can link multiple identity providers to a single application account. Account linking must be performed by an authenticated user. Users cannot unlink their only authentication method.

### Floci Limitations

Floci may not fully emulate external Google/Apple federation. For local development:
- Use direct Cognito authentication (username/password) for testing
- SSO provider callbacks may need to be tested against real AWS Cognito
- JWT validation works with Floci-emulated Cognito

## AWS Services

### Cognito

The application uses AWS Cognito for authentication. Floci emulates Cognito locally.

### S3

S3 is used for file storage. The `S3Service` provides:
- Upload files
- Download files
- Delete files
- Generate presigned URLs

### EventBridge

EventBridge is used for event-driven processing. The `EventBridgeService` provides:
- Publish events
- Schedule rules

### Celery

Celery workers process background tasks. Celery Beat handles scheduled jobs.

Business logic lives in reusable task functions that can be triggered by:
- Celery Beat
- API endpoints
- Manual execution

## Docker Networking

| From              | PostgreSQL | Redis  | Floci/AWS  |
|-------------------|-----------|--------|------------|
| Host machine      | localhost:5432 | localhost:6379 | localhost:4566 |
| API container     | postgres:5432 | redis:6379 | floci:4566 |
| Celery container  | postgres:5432 | redis:6379 | floci:4566 |

**Never use `localhost` from inside containers for other services.**

## Floci Configuration

Floci runs on port 4566 and emulates AWS services locally.

Floci requires access to the Docker socket for some services:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - ./data:/app/data
```

## AWS Infrastructure

### VPC

- VPC with public and private subnets
- Internet Gateway for public subnets
- NAT Gateways for private subnets
- Route tables and associations

### RDS

- PostgreSQL 16 on RDS
- Private subnet deployment
- Storage encryption enabled
- Backup retention configured
- Security groups restrict access to API/worker tasks only

### ElastiCache Redis

- Redis cluster in private subnets
- Encryption at rest and in transit
- Security groups restrict access to API/worker tasks only

### Cognito

- User Pool with email sign-in
- Password policy enforced
- App Client with secret
- Email verification enabled

### S3

- Bucket with versioning
- Server-side encryption (AES256)
- Public access blocked
- Lifecycle rules configurable

### ECS/Fargate

- API service (Fargate)
- Worker service (Fargate)
- Private subnet deployment
- Task roles with least-privilege permissions
- CloudWatch logging

### ALB

- Application Load Balancer
- Health checks on `/health`
- HTTP listener on port 80
- Target group for API service

### IAM

- ECS task execution role (ECR, CloudWatch, Secrets Manager)
- ECS task role (application permissions)
- Least-privilege policies
- No AdministratorAccess

### CloudWatch

- ECS log groups
- Configurable retention period

## CI/CD

### GitHub Actions Workflows

- `ci.yml` - Lint, format check, type check, tests, Docker build
- `test.yml` - Run tests against PostgreSQL
- `build.yml` - Build and test Docker image
- `terraform-plan.yml` - Terraform plan on PR/push
- `terraform-apply-dev.yml` - Apply Terraform to dev on push to develop
- `deploy-dev.yml` - Deploy to dev environment

## Testing

### Unit Tests

```bash
make test
```

### Integration Tests

Integration tests run against the development environment (PostgreSQL + Redis + Floci).

## Security

- Passwords are never stored in PostgreSQL
- JWT access tokens are never logged
- Cognito client secrets are stored in AWS Secrets Manager
- Database credentials are stored in AWS Secrets Manager
- IAM roles use least-privilege permissions
- RDS is deployed in private subnets
- ElastiCache is deployed in private subnets
- S3 blocks public access
- Docker socket is only mounted into Floci, not into FastAPI or Celery containers

## Troubleshooting

### Floci Docker Socket Problems

1. Check socket mount: `/var/run/docker.sock:/var/run/docker.sock`
2. Verify permissions: `ls -la /var/run/docker.sock`
3. On Docker Desktop, ensure the socket path matches your OS

### PostgreSQL Connection Issues

- Ensure you're using `postgres:5432` from inside containers
- Check `DATABASE_URL` in `.env`
- Run `docker compose -f docker-compose.dev.yml logs postgres`

### JWT Validation Issues

- Ensure `JWT_ISSUER` matches the Cognito issuer
- Ensure `AWS_ENDPOINT_URL` is set correctly for local development

### Terraform Issues

- Ensure AWS credentials are configured: `aws sts get-caller-identity`
- Ensure S3 backend bucket and DynamoDB table exist for state locking
- Run `terraform validate` to check configuration errors

## Limitations

- Floci does not perfectly emulate all AWS services. Some EventBridge features may not work locally.
- Floci state is ephemeral. User registrations and S3 objects are lost when the container restarts unless persisted.
