variable "terraform_state_bucket" {
  description = "S3 bucket that holds terraform state object"
  type        = string
  default     = "my-terraform-state-bucket"
}

variable "environment" {
  description = "Environment for the deployment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}