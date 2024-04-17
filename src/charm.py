#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Integrator charm to provide a fiveg_gnb_identity."""

import logging
from typing import Optional, cast

import ops
from charms.sdcore_gnbsim_k8s.v0.fiveg_gnb_identity import (  # type: ignore[import]
    GnbIdentityProvides,
)
from ops import ActiveStatus, BlockedStatus, CollectStatusEvent

logger = logging.getLogger(__name__)

GNB_IDENTITY_RELATION_NAME = "fiveg_gnb_identity"


class SdcoreGnbIntegratorCharm(ops.CharmBase):
    """Charm for gNB Integrator Service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self._gnb_identity_provider = GnbIdentityProvides(self, GNB_IDENTITY_RELATION_NAME)
        self.framework.observe(
            self._gnb_identity_provider.on.fiveg_gnb_identity_request,
            self._on_config_changed,
        )

    def _on_collect_unit_status(self, event: CollectStatusEvent):
        """Checks the unit status and set it when CollectStatusEvent is fired.

        Args:
            event: CollectStatusEvent
        """
        if invalid_configs := self._get_invalid_configs():
            event.add_status(
                BlockedStatus(f"The following configurations are not valid: {invalid_configs}")
            )
            logger.info("The following configurations are not valid: %s", invalid_configs)
            return
        event.add_status(ActiveStatus())

    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        """Publish new gNB configuration via the relation databag"""

        self._update_fiveg_gnb_identity_relation_data()
        self.unit.status = ActiveStatus()

    def _update_fiveg_gnb_identity_relation_data(self) -> None:
        """Publish GNB name and TAC in the `fiveg_gnb_identity` relation data bag."""
        if not self.unit.is_leader():
            return
        fiveg_gnb_identity_relations = self.model.relations.get(GNB_IDENTITY_RELATION_NAME)
        if not fiveg_gnb_identity_relations:
            logger.info("No %s relations found.", GNB_IDENTITY_RELATION_NAME)
            return

        tac = self._get_tac_as_int()
        if not tac:
            logger.error(
                "TAC value cannot be published on the %s relation", GNB_IDENTITY_RELATION_NAME
            )
            return
        for gnb_identity_relation in fiveg_gnb_identity_relations:
            self._gnb_identity_provider.publish_gnb_identity_information(
                relation_id=gnb_identity_relation.id, gnb_name=self._gnb_name, tac=tac
            )

    def _get_invalid_configs(self) -> list[str]:
        """Get a list of invalid Juju configurations."""
        invalid_configs = []
        if not self._get_tac_from_config() or not self._get_tac_as_int():
            invalid_configs.append("tac")
        return invalid_configs

    def _get_tac_from_config(self) -> Optional[str]:
        return cast(Optional[str], self.model.config.get("tac"))

    def _get_tac_as_int(self) -> Optional[int]:
        """Convert the TAC value in the config to an integer.

        Returns:
            TAC as an integer. None if the config value is invalid.
        """
        tac = None
        try:
            tac = int(self.model.config.get("tac"), 16)  # type: ignore[arg-type]
        except ValueError:
            logger.error("Invalid TAC value in config: it cannot be converted to integer.")
        return tac

    @property
    def _gnb_name(self) -> str:
        """The gNB's name contains the model name and the app name.

        Returns:
            str: the gNB's name.
        """
        return f"{self.model.name}-gnb-{self.app.name}"


if __name__ == "__main__":  # pragma: nocover
    ops.main(SdcoreGnbIntegratorCharm)  # type: ignore
