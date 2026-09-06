# Run ONCE before infra/. Keep this local state privately backed up.
terraform {
  required_version = "~> 1.13.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "0.225.0"
    }
  }
}
variable "folder_id" {
  type = string
}
variable "state_bucket" {
  type = string
}
provider "yandex" {
  folder_id = var.folder_id
}
resource "yandex_storage_bucket" "state" {
  bucket        = var.state_bucket
  folder_id     = var.folder_id
  force_destroy = false
  anonymous_access_flags {
    read        = false
    list        = false
    config_read = false
  }
  versioning {
    enabled = true
  }
  lifecycle {
    prevent_destroy = true
  }
}
output "state_bucket" {
  value = yandex_storage_bucket.state.bucket
}
