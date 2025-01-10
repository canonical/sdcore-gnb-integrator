# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "gnb" {
  name  = var.app_name
  model = var.model

  charm {
    name    = "sdcore-gnb-integrator"
    channel = var.channel
    revision = var.revision
    base     = var.base
  }

  constraints = var.constraints
  resources   = var.resources
  units       = var.units
}
