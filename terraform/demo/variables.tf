variable "aws_region" {
  description = "AWS region used by the demo infrastructure."
  type        = string
  default     = "ca-central-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket used by the demo application."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "demo"
}