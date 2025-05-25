module "storage" {
  source          = "./storage"
  bucket_name     = var.bucket_name
  project_id      = "citi-bike-459310"
  bucket_location = var.bucket_location

}