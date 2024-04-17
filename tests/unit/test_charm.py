# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
#

import unittest
from unittest.mock import call, patch

import ops
import ops.testing
from charm import SdcoreGnbIntegratorCharm
from ops.model import ActiveStatus, BlockedStatus

GNB_IDENTITY_LIB_PATH = "charms.sdcore_gnbsim_k8s.v0.fiveg_gnb_identity"


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.namespace = "whatever"
        self.harness = ops.testing.Harness(SdcoreGnbIntegratorCharm)
        self.harness.set_model_name(name=self.namespace)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_given_default_config_when_config_changed_then_status_is_active(self):
        self.harness.evaluate_status()
        self.harness.update_config(key_values={})
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus())

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def test_given_tac_when_fiveg_gnb_identity_relation_created_then_gnb_name_and_tac_are_published(  # noqa: E501
        self, patched_publish_gnb_identity
    ):
        self.harness.set_leader(is_leader=True)

        test_tac = "012"
        test_tac_int = 18
        expected_gnb_name = f"{self.namespace}-gnb-{self.harness.charm.app.name}"
        self.harness.update_config(key_values={"tac": test_tac})

        relation_id = self.harness.add_relation("fiveg_gnb_identity", "gnb_identity_requirer_app")
        self.harness.add_relation_unit(relation_id, "gnb_identity_requirer_app/0")

        patched_publish_gnb_identity.assert_called_once_with(
            relation_id=relation_id, gnb_name=expected_gnb_name, tac=test_tac_int
        )

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def test_given_no_tac_in_config_when_fiveg_gnb_identity_relation_is_added_then_default_tac_is_published(  # noqa: E501
        self, patched_publish_gnb_identity
    ):
        self.harness.set_leader(is_leader=True)

        relation_id = self.harness.add_relation("fiveg_gnb_identity", "gnb_identity_requirer_app")
        self.harness.add_relation_unit(relation_id, "gnb_identity_requirer_app/0")
        expected_gnb_name = f"{self.namespace}-gnb-{self.harness.charm.app.name}"
        default_tac_int = 1

        patched_publish_gnb_identity.assert_called_once_with(
            relation_id=relation_id, gnb_name=expected_gnb_name, tac=default_tac_int
        )

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def test_given_tac_is_not_hexadecimal_when_update_config_then_charm_status_is_blocked(
        self,
        _,
    ):
        self.harness.set_leader(is_leader=True)

        test_tac = "gg"
        self.harness.update_config(key_values={"tac": test_tac})
        self.harness.evaluate_status()
        self.assertEqual(
            self.harness.charm.unit.status, BlockedStatus("Configurations are invalid: ['tac']")
        )

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def test_given_tac_is_not_hexadecimal_when_fiveg_gnb_identity_relation_is_added_then_gnb_identity_is_not_published(  # noqa: E501
        self, patched_publish_gnb_identity
    ):
        self.harness.set_leader(is_leader=True)

        test_tac = "gg"
        self.harness.update_config(key_values={"tac": test_tac})
        relation_id = self.harness.add_relation("fiveg_gnb_identity", "gnb_identity_requirer_app")
        self.harness.add_relation_unit(relation_id, "gnb_identity_requirer_app/0")

        patched_publish_gnb_identity.assert_not_called()

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def tests_given_unit_is_not_leader_when_fiveg_gnb_identity_relation_is_added_then_gnb_identity_is_not_published(  # noqa: E501
        self, patched_publish_gnb_identity
    ):
        self.harness.set_leader(is_leader=False)
        relation_id = self.harness.add_relation("fiveg_gnb_identity", "gnb_identity_requirer_app")
        self.harness.add_relation_unit(relation_id, "gnb_identity_requirer_app/0")

        patched_publish_gnb_identity.assert_not_called()

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def test_given_fiveg_gnb_identity_relation_exists_when_tac_config_changed_then_new_tac_is_published(  # noqa: E501
        self, patched_publish_gnb_identity
    ):
        self.harness.set_leader(is_leader=True)

        relation_id = self.harness.add_relation("fiveg_gnb_identity", "gnb_identity_requirer_app")
        self.harness.add_relation_unit(relation_id, "gnb_identity_requirer_app/0")
        default_tac_int = 1
        test_tac = "F"
        test_tac_int = 15
        expected_gnb_name = f"{self.namespace}-gnb-{self.harness.charm.app.name}"

        expected_calls = [
            call(relation_id=relation_id, gnb_name=expected_gnb_name, tac=default_tac_int),
            call(relation_id=relation_id, gnb_name=expected_gnb_name, tac=test_tac_int),
        ]
        self.harness.update_config(key_values={"tac": test_tac})
        patched_publish_gnb_identity.assert_has_calls(expected_calls)

    @patch(f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information")
    def test_given_fiveg_gnb_identity_relation_not_created_when_update_config_does_not_publish_gnb_identity(  # noqa: E501
        self, patched_publish_gnb_identity
    ):
        self.harness.set_leader(is_leader=True)
        self.harness.update_config(key_values={"tac": "12345"})

        patched_publish_gnb_identity.assert_not_called()
