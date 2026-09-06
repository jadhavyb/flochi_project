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
  description = "Security group ID for ElastiCache"
}

variable "node_type" {
  type        = string
  default     = "cache.t3.micro"
  description = "ElastiCache node type"
}

variable "number_cache_clusters" {
  type        = number
  default     = 1
  description = "Number of cache clusters"
}

variable "engine_version" {
  type        = string
  default     = "7.1"
  description = "Redis engine version"
}
