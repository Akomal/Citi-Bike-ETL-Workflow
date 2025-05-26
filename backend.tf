# backend.tf
terraform {
  backend "gcs" {
    bucket = "tt-state01" # Your existing bucket name

  }
}