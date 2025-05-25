module "storage" {
  source          = "./storage"
  bucket_name     = var.bucket_name
  project_id      = var.project_id
  bucket_location = var.bucket_location
}