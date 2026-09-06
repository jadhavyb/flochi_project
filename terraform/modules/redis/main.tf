resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.project_name}-redis-subnet-group"
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id         = "${var.project_name}-redis"
  description                  = "Redis cluster for ${var.project_name}"
  engine                       = "redis"
  engine_version               = var.engine_version
  node_type                    = var.node_type
  number_cache_clusters        = var.number_cache_clusters
  port                         = 6379
  subnet_group_name            = aws_elasticache_subnet_group.main.name
  security_group_ids           = [var.security_group_id]
  at_rest_encryption_enabled   = true
  transit_encryption_enabled   = true

  tags = {
    Name = "${var.project_name}-redis"
  }
}
