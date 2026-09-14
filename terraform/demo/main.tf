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

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "application_data" {
  bucket = aws_s3_bucket.application_data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "application_data" {
  bucket = aws_s3_bucket.application_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

data "aws_iam_policy_document" "application_data" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:*"
    ]

    resources = [
      aws_s3_bucket.application_data.arn,
      "${aws_s3_bucket.application_data.arn}/*"
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "application_data" {
  bucket = aws_s3_bucket.application_data.id
  policy = data.aws_iam_policy_document.application_data.json
}

resource "aws_kms_key" "application_data" {
  description             = "KMS key for application data S3 bucket"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Environment = var.environment
    Project     = "agentic-devsecops-demo"
  }
}

resource "aws_kms_alias" "application_data" {
  name          = "alias/agentic-devsecops-application-data"
  target_key_id = aws_kms_key.application_data.key_id
}

resource "aws_s3_bucket_server_side_encryption_configuration" "application_data" {
  bucket = aws_s3_bucket.application_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.application_data.arn
    }

    bucket_key_enabled = true
  }
}