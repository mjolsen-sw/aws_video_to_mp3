terraform {
  backend "s3" {
    bucket         = "mjolsen-video-to-mp3-terraform-state"
    key            = "envs/dev/terraform.tfstate"
    region         = "us-west-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}