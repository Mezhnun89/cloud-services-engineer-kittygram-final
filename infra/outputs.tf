output "vm_ip" {
  value = yandex_vpc_address.kittygram.external_ipv4_address[0].address
}
output "vm_id" {
  value = yandex_compute_instance.kittygram.id
}
output "app_url" {
  value = "http://${yandex_vpc_address.kittygram.external_ipv4_address[0].address}:${var.gateway_port}"
}
output "gateway_port" {
  value = var.gateway_port
}
output "ssh_user" {
  value = "deploy"
}
