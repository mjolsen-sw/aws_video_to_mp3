variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "terraform_state_bucket" {
  description = "S3 bucket that holds terraform state object"
  type        = string
  default     = "my-terraform-state-bucket"
}