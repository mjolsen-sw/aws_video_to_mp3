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

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "environment" {
  description = "Environment for the deployment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}
