module "storage" {
  source          = "./storage"
  bucket_name     = var.bucket_name
  project         = var.project_id
  bucket_location = var.bucket_location

}