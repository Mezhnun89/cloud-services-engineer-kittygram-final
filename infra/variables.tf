variable "cloud_id" {
  type = string
}
variable "folder_id" {
  type = string
}
variable "zone" {
  type    = string
  default = "ru-central1-a"
}
variable "ssh_public_key" {
  type = string
  validation {
    condition     = can(regex("^ssh-(ed25519|rsa) [A-Za-z0-9+/=]+", trimspace(var.ssh_public_key)))
    error_message = "Provide an OpenSSH public key, never a private key."
  }
}
variable "ssh_cidrs" {
  description = "GitHub hosted runners have changing IPs; restrict if using a fixed runner."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
variable "gateway_port" {
  type    = number
  default = 9000
  validation {
    condition     = var.gateway_port >= 1024 && var.gateway_port <= 65535 && floor(var.gateway_port) == var.gateway_port
    error_message = "Use an integer port between 1024 and 65535."
  }
}
variable "image_id" {
  description = "Optional pinned Ubuntu 24.04 image ID; otherwise resolve the family."
  type        = string
  default     = null
}
