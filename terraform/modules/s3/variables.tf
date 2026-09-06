variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev)"
}

variable "versioning_enabled" {
  type        = bool
  default     = true
  description = "Enable S3 versioning"
}
