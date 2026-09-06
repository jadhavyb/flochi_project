variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs"
}

variable "security_group_id" {
  type        = string
  description = "Security group ID for RDS"
}

variable "database_name" {
  type        = string
  default     = "demo_db"
  description = "Database name"
}

variable "username" {
  type        = string
  default     = "postgres"
  description = "Database master username"
}

variable "password" {
  type        = string
  description = "Database master password"
  sensitive   = true
}

variable "instance_class" {
  type        = string
  default     = "db.t3.micro"
  description = "RDS instance class"
}

variable "allocated_storage" {
  type        = number
  default     = 20
  description = "Allocated storage in GB"
}

variable "engine_version" {
  type        = string
  default     = "16"
  description = "PostgreSQL engine version"
}

variable "backup_retention_period" {
  type        = number
  default     = 7
  description = "Backup retention period in days"
}

variable "multi_az" {
  type        = bool
  default     = false
  description = "Enable multi-AZ deployment"
}

variable "deletion_protection" {
  type        = bool
  default     = false
  description = "Enable deletion protection"
}

variable "skip_final_snapshot" {
  type        = bool
  default     = true
  description = "Skip final snapshot before destroy"
}
