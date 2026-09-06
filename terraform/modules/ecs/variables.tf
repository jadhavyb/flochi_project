variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev)"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs"
}

variable "ecs_task_execution_role_arn" {
  type        = string
  description = "ECS task execution role ARN"
}

variable "ecs_task_role_arn" {
  type        = string
  description = "ECS task role ARN"
}

variable "target_group_arn" {
  type        = string
  description = "ALB target group ARN"
}

variable "database_url" {
  type        = string
  description = "Database URL"
  sensitive   = true
}

variable "redis_url" {
  type        = string
  description = "Redis URL"
}

variable "cognito_user_pool_id" {
  type        = string
  description = "Cognito User Pool ID"
}

variable "cognito_client_id" {
  type        = string
  description = "Cognito App Client ID"
}

variable "cognito_client_secret_arn" {
  type        = string
  description = "Cognito client secret ARN from Secrets Manager"
}

variable "db_secret_arn" {
  type        = string
  description = "Database secret ARN from Secrets Manager"
}

variable "s3_bucket_name" {
  type        = string
  description = "S3 bucket name"
}

variable "api_image_url" {
  type        = string
  description = "API Docker image URL"
}

variable "worker_image_url" {
  type        = string
  description = "Worker Docker image URL"
}

variable "api_cpu" {
  type        = string
  default     = "256"
  description = "API task CPU units"
}

variable "api_memory" {
  type        = string
  default     = "512"
  description = "API task memory in MB"
}

variable "worker_cpu" {
  type        = string
  default     = "256"
  description = "Worker task CPU units"
}

variable "worker_memory" {
  type        = string
  default     = "512"
  description = "Worker task memory in MB"
}

variable "api_desired_count" {
  type        = number
  default     = 2
  description = "Desired count for API service"
}

variable "worker_desired_count" {
  type        = number
  default     = 1
  description = "Desired count for worker service"
}

variable "api_security_group_id" {
  type        = string
  description = "Security group ID for API tasks"
}

variable "worker_security_group_id" {
  type        = string
  description = "Security group ID for worker tasks"
}
