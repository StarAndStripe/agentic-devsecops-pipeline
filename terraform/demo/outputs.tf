output "bucket_name" {
  description = "Name of the application data bucket."
  value       = aws_s3_bucket.application_data.id
}