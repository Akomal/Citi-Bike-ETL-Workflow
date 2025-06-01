# backend.tf
terraform {
  backend "gcs" {
    bucket = "tf-bronze" # Your existing bucket name

  }
}