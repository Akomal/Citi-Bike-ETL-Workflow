# backend.tf
terraform {
  backend "gcs" {
    bucket = "tt-states" # Your existing bucket name

  }
}