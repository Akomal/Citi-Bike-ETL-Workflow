resource "google_storage_bucket" "storage-buckets" {
  name          = var.bucket_name
  location      = var.bucket_location
  project_id      = var.project_id
  force_destroy = true

  public_access_prevention = "enforced"
}