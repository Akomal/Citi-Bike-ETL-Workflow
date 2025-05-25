module "storage" {
  source          = "./storage"
  bucket_name     = var.bucket_name
  bucket_location = var.bucket_location
}