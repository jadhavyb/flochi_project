output "vpc_id" {
  value = module.vpc.vpc_id
}

output "public_subnet_ids" {
  value = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "ecs_cluster_id" {
  value = module.ecs.ecs_cluster_id
}

output "alb_dns_name" {
  value = module.alb.alb_dns_name
}

output "rds_endpoint" {
  value = module.rds.rds_endpoint
}

output "redis_endpoint" {
  value = module.redis.redis_endpoint
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_app_client_id" {
  value = module.cognito.app_client_id
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}

output "api_repository_url" {
  value = module.ecr.api_repository_url
}

output "worker_repository_url" {
  value = module.ecr.worker_repository_url
}

output "db_secret_arn" {
  value = module.secrets.db_secret_arn
}

output "cognito_client_secret_arn" {
  value = module.secrets.cognito_client_secret_arn
}
