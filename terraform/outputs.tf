# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.gnb.name
}

# Provided integration endpoints

output "fiveg_gnb_identity_endpoint" {
  description = "Name of the endpoint used to provide information about represented gNB."
  value       = "fiveg_gnb_identity"
}
