# backend.tf
terraform {
  backend "gcs" {
    bucket = "tt-state09" # Your existing bucket name

  }
}