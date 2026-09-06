variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev)"
}

variable "db_username" {
  type        = string
  description = "Database username"
  default     = "postgres"
}

variable "db_password" {
  type        = string
  description = "Database password"
  sensitive   = true
}

variable "cognito_client_secret_value" {
  type        = string
  description = "Cognito client secret value"
  sensitive   = true
}
