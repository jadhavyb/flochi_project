terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "../../modules/vpc"

  project_name      = var.project_name
  vpc_cidr          = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones = var.availability_zones
}

module "ecr" {
  source = "../../modules/ecr"
  project_name = var.project_name
}

module "iam" {
  source = "../../modules/iam"
  project_name = var.project_name
}

module "rds" {
  source = "../../modules/rds"

  project_name      = var.project_name
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_id = aws_security_group.rds.id
  password          = var.db_password
}

module "redis" {
  source = "../../modules/redis"

  project_name      = var.project_name
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_id = aws_security_group.redis.id
}

module "cognito" {
  source = "../../modules/cognito"
  project_name = var.project_name
}

module "s3" {
  source = "../../modules/s3"
  project_name = var.project_name
  environment  = var.environment
}

module "eventbridge" {
  source = "../../modules/eventbridge"
  project_name = var.project_name
  environment  = var.environment
}

module "secrets" {
  source = "../../modules/secrets"
  project_name = var.project_name
  environment  = var.environment
  cognito_client_secret_value = module.cognito.app_client_secret
  db_password                 = var.db_password
}

module "alb" {
  source = "../../modules/alb"
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_id = aws_security_group.alb.id
}

module "ecs" {
  source = "../../modules/ecs"
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region
  vpc_id       = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids = module.vpc.public_subnet_ids
  ecs_task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  ecs_task_role_arn = module.iam.ecs_task_role_arn
  target_group_arn = module.alb.target_group_arn
  database_url = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${module.rds.rds_endpoint}:5432/${var.database_name}"
  redis_url = "redis://${module.redis.redis_endpoint}:6379/0"
  cognito_user_pool_id = module.cognito.user_pool_id
  cognito_client_id = module.cognito.app_client_id
  cognito_client_secret_arn = module.secrets.cognito_client_secret_arn
  db_secret_arn = module.secrets.db_secret_arn
  s3_bucket_name = module.s3.bucket_name
  api_image_url = module.ecr.api_repository_url
  worker_image_url = module.ecr.worker_repository_url
  api_security_group_id = aws_security_group.api.id
  worker_security_group_id = aws_security_group.worker.id
}
