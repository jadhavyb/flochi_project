resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  tags = {
    Name        = "${var.project_name}-${var.environment}-cluster"
    Environment = var.environment
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = "${var.api_image_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "APP_ENV"
          value = var.environment
        }
        {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        {
          name  = "REDIS_URL"
          value = var.redis_url
        }
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
        {
          name  = "COGNITO_USER_POOL_ID"
          value = var.cognito_user_pool_id
        }
        {
          name  = "COGNITO_CLIENT_ID"
          value = var.cognito_client_id
        }
        {
          name  = "CELERY_BROKER_URL"
          value = var.redis_url
        }
        {
          name  = "S3_BUCKET_NAME"
          value = var.s3_bucket_name
        }
      ]
      secrets = [
        {
          name      = "COGNITO_CLIENT_SECRET"
          valueFrom = var.cognito_client_secret_arn
        }
        {
          name      = "DATABASE_URL"
          valueFrom = var.db_secret_arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.project_name}-${var.environment}"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-api"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.api_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "api"
    container_port   = 8000
  }

  tags = {
    Name        = "${var.project_name}-api-service"
    Environment = var.environment
  }
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = "${var.worker_image_url}:latest"
      essential = true
      command   = ["celery", "-A", "app.worker.celery_app", "worker", "--loglevel=info"]
      environment = [
        {
          name  = "APP_ENV"
          value = var.environment
        }
        {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        {
          name  = "REDIS_URL"
          value = var.redis_url
        }
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
        {
          name  = "COGNITO_USER_POOL_ID"
          value = var.cognito_user_pool_id
        }
        {
          name  = "COGNITO_CLIENT_ID"
          value = var.cognito_client_id
        }
        {
          name  = "CELERY_BROKER_URL"
          value = var.redis_url
        }
        {
          name  = "S3_BUCKET_NAME"
          value = var.s3_bucket_name
        }
      ]
      secrets = [
        {
          name      = "COGNITO_CLIENT_SECRET"
          valueFrom = var.cognito_client_secret_arn
        }
        {
          name      = "DATABASE_URL"
          valueFrom = var.db_secret_arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.project_name}-${var.environment}"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "worker"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-worker"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-worker-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.worker_security_group_id]
    assign_public_ip = false
  }

  tags = {
    Name        = "${var.project_name}-worker-service"
    Environment = var.environment
  }
}
