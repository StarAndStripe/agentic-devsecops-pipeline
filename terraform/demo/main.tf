terraform {
  required_version = ">= 1.8.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "application_data" {
  bucket = var.bucket_name

  tags = {
    Environment = var.environment
    Project     = "agentic-devsecops-demo"
  }
}

resource "aws_s3_bucket_public_access_block" "application_data" {
  bucket = aws_s3_bucket.application_data.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "application_data" {
  depends_on = [
    aws_s3_bucket_ownership_controls.application_data,
    aws_s3_bucket_public_access_block.application_data
  ]

  bucket = aws_s3_bucket.application_data.id
  acl    = "public-read"
}

resource "aws_s3_bucket_ownership_controls" "application_data" {
  bucket = aws_s3_bucket.application_data.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}