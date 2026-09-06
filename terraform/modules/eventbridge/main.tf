resource "aws_cloudwatch_event_bus" "main" {
  name = "${var.project_name}-${var.environment}-events"

  tags = {
    Name        = "${var.project_name}-${var.environment}-events"
    Environment = var.environment
  }
}
