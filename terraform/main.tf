# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "gnb" {
  name  = var.app_name
  model = var.model_name

  charm {
    name    = "sdcore-gnb-integrator"
    channel = var.channel
  }
  config = var.config
  units  = 1
}
