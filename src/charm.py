#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integrator charm to provide a fiveg_gnb_identity."""

import logging

import ops
from charms.sdcore_nms_k8s.v0.fiveg_core_gnb import FivegCoreGnbRequires
from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, EventBase, WaitingStatus

logger = logging.getLogger(__name__)

CORE_GNB_RELATION_NAME = "fiveg_core_gnb"


class SdcoreGnbIntegratorCharm(ops.CharmBase):
    """Charm for gNB Integrator Service."""

    def __init__(self, *args):
        super().__init__(*args)
        self._core_gnb_requirer = FivegCoreGnbRequires(self, CORE_GNB_RELATION_NAME)
        self.framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)
        self.framework.observe(self.on.update_status, self._configure)
        self.framework.observe(
            self.on[CORE_GNB_RELATION_NAME].relation_changed,
            self._configure,
        )

    def _on_collect_unit_status(self, event: CollectStatusEvent):
        """Check the unit status and set it when CollectStatusEvent is fired.

        Args:
            event: CollectStatusEvent
        """
        if not self._relation_created(CORE_GNB_RELATION_NAME):
            event.add_status(
                BlockedStatus(f"Waiting for {CORE_GNB_RELATION_NAME} relation to be created")
            )
            logger.info("Waiting for %s relation to be created", CORE_GNB_RELATION_NAME)
            return
        if not self._core_gnb_requirer.tac or not self._core_gnb_requirer.plmns:
            event.add_status(WaitingStatus("Waiting for TAC and PLMNs configuration"))
            return
        if not self._is_gnb_name_published():
            event.add_status(
                BlockedStatus(
                    "Invalid configuration: gNB name is missing from the relation"
                )
            )
            return
        event.add_status(
            ActiveStatus(
                f"PLMNs: {','.join([str(plmn.asdict()) for plmn in self._core_gnb_requirer.plmns])}, "  # noqa: E501
                f"TAC: {self._core_gnb_requirer.tac}"
            )
        )

    def _configure(self, _: EventBase) -> None:
        """Publish gNB name `fiveg_core_gnb` relation data bag."""
        if not self.unit.is_leader():
            return
        if not self._relation_created(CORE_GNB_RELATION_NAME):
            logger.info("No %s relations found.", CORE_GNB_RELATION_NAME)
            return

        try:
            self._core_gnb_requirer.publish_gnb_information(gnb_name=self._gnb_name)
        except ValueError:
            return

    def _relation_created(self, relation_name: str) -> bool:
        """Return whether a given Juju relation was created.

        Args:
            relation_name (str): Relation name

        Returns:
            bool: Whether the relation was created.
        """
        return bool(self.model.relations.get(relation_name))

    @property
    def _gnb_name(self) -> str:
        """The gNB's name contains the model name and the app name.

        Returns:
            str: the gNB's name.
        """
        return f"{self.model.name}-gnb-{self.app.name}"

    def _is_gnb_name_published(self) -> bool:
        relation = self.model.get_relation(CORE_GNB_RELATION_NAME)
        if not relation:
            return False
        return relation.data[self.app].get("gnb-name") is not None


if __name__ == "__main__":  # pragma: nocover
    ops.main(SdcoreGnbIntegratorCharm)  # type: ignore
