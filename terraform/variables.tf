variable "project_id" {
  type        = string
  description = "GCP project ID where the bucket will be created"
}

variable "bucket_names" {
  type        = list(string)
  description = "Names of the GCS buckets"
}

variable "bucket_location" {
  type        = string
  description = "GCS bucket location (region or multi-region)"
  default     = "EU"
}

variable "composer_region" {
  type        = string
  description = "Region for Composer environment"
  default     = "europe-west4" # Same as bucket_location by default
}

variable "citibike_composer_name" {
  type        = string
  description = "name for Composer environment"
}

variable "composer_service_account" {
  description = "The email address of the service account used by Cloud Composer"
  type        = string
}
