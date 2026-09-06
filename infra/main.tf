data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2404-lts"
}

resource "yandex_vpc_network" "kittygram" {
  name = "kittygram-network"
}

resource "yandex_vpc_subnet" "kittygram" {
  name           = "kittygram-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.kittygram.id
  v4_cidr_blocks = ["10.42.0.0/24"]
}

resource "yandex_vpc_security_group" "kittygram" {
  name       = "kittygram-security-group"
  network_id = yandex_vpc_network.kittygram.id
  ingress {
    description    = "SSH key authentication"
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = var.ssh_cidrs
  }
  ingress {
    description    = "Kittygram HTTP gateway"
    protocol       = "TCP"
    port           = var.gateway_port
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description    = "All outbound traffic"
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_address" "kittygram" {
  name = "kittygram-public-ip"
  external_ipv4_address {
    zone_id = var.zone
  }
}

resource "yandex_compute_instance" "kittygram" {
  name        = "kittygram"
  hostname    = "kittygram"
  platform_id = "standard-v3"
  zone        = var.zone
  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }
  boot_disk {
    initialize_params {
      image_id = coalesce(var.image_id, data.yandex_compute_image.ubuntu.id)
      type     = "network-ssd"
      size     = 20
    }
  }
  network_interface {
    subnet_id          = yandex_vpc_subnet.kittygram.id
    nat                = true
    nat_ip_address     = yandex_vpc_address.kittygram.external_ipv4_address[0].address
    security_group_ids = [yandex_vpc_security_group.kittygram.id]
  }
  metadata = {
    user-data = templatefile("${path.module}/cloud-init.yaml.tftpl", {
      ssh_public_key = jsonencode(trimspace(var.ssh_public_key))
    })
    serial-port-enable = "1"
  }
  # A newer image in the family must not replace a VM containing the database.
  lifecycle {
    ignore_changes = [boot_disk[0].initialize_params[0].image_id]
  }
}
