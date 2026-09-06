terraform {
  required_version = "~> 1.13.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "0.225.0"
    }
  }
  backend "s3" {
    endpoints                   = { s3 = "https://storage.yandexcloud.net" }
    key                         = "kittygram/production.tfstate"
    region                      = "ru-central1"
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }
}

provider "yandex" {
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
}
