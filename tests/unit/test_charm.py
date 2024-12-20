# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
#

from unittest.mock import call, patch

import pytest
from ops import testing
from ops.model import ActiveStatus, BlockedStatus

from charm import SdcoreGnbIntegratorCharm

GNB_IDENTITY_LIB_PATH = "charms.sdcore_gnbsim_k8s.v0.fiveg_gnb_identity"
NAMESPACE = "whatever"

class TestCharm:

    patcher_publish_gnb_identity = patch(
        f"{GNB_IDENTITY_LIB_PATH}.GnbIdentityProvides.publish_gnb_identity_information"
    )

    @pytest.fixture()
    def setUp(self):
        self.mock_publish_gnb_identity = TestCharm.patcher_publish_gnb_identity.start()

    @staticmethod
    def tearDown() -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def harness_setup(self, setUp, request):
        self.harness: testing.Harness[SdcoreGnbIntegratorCharm] = (
            testing.Harness(SdcoreGnbIntegratorCharm)
        )
        self.harness.set_model_name(name=NAMESPACE)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()
        yield self.harness
        self.harness.cleanup()
        request.addfinalizer(self.tearDown)

    def add_fiveg_gnb_identity_relation(self) -> int:
        relation_id = self.harness.add_relation("fiveg_gnb_identity", "gnb_identity_requirer_app")
        self.harness.add_relation_unit(relation_id, "gnb_identity_requirer_app/0")
        return relation_id

    def test_given_default_config_then_status_is_active(self):
        self.harness.evaluate_status()
        assert self.harness.charm.unit.status == ActiveStatus()

    def test_given_tac_when_fiveg_gnb_identity_relation_created_then_gnb_name_and_tac_are_published(  # noqa: E501
        self,
    ):
        test_tac = "012"
        test_tac_int = 18
        expected_gnb_name = f"{NAMESPACE}-gnb-{self.harness.charm.app.name}"
        self.harness.update_config(key_values={"tac": test_tac})

        relation_id = self.add_fiveg_gnb_identity_relation()

        self.mock_publish_gnb_identity.assert_called_once_with(
            relation_id=relation_id, gnb_name=expected_gnb_name, tac=test_tac_int
        )

    def test_given_no_tac_in_config_when_fiveg_gnb_identity_relation_is_added_then_default_tac_is_published(  # noqa: E501
        self,
    ):
        relation_id = self.add_fiveg_gnb_identity_relation()
        expected_gnb_name = f"{NAMESPACE}-gnb-{self.harness.charm.app.name}"
        default_tac_int = 1

        self.mock_publish_gnb_identity.assert_called_once_with(
            relation_id=relation_id, gnb_name=expected_gnb_name, tac=default_tac_int
        )

    def test_given_tac_is_not_hexadecimal_when_update_config_then_charm_status_is_blocked(self):
        invalid_tac = "gg"
        self.harness.update_config(key_values={"tac": invalid_tac})
        self.harness.evaluate_status()

        assert self.harness.charm.unit.status == BlockedStatus(
            "The following configurations are not valid: ['tac']"
        )

    def test_given_tac_is_not_hexadecimal_when_fiveg_gnb_identity_relation_is_added_then_gnb_identity_is_not_published(  # noqa: E501
        self,
    ):
        invalid_tac = "gg"
        self.harness.update_config(key_values={"tac": invalid_tac})
        self.add_fiveg_gnb_identity_relation()

        self.mock_publish_gnb_identity.assert_not_called()

    def tests_given_unit_is_not_leader_when_fiveg_gnb_identity_relation_is_added_then_gnb_identity_is_not_published(  # noqa: E501
        self,
    ):
        self.harness.set_leader(is_leader=False)
        self.add_fiveg_gnb_identity_relation()

        self.mock_publish_gnb_identity.assert_not_called()

    def test_given_fiveg_gnb_identity_relation_exists_when_tac_config_changed_then_new_tac_is_published(  # noqa: E501
        self,
    ):
        relation_id = self.add_fiveg_gnb_identity_relation()
        default_tac_int = 1
        test_tac = "F"
        test_tac_int = 15
        expected_gnb_name = f"{NAMESPACE}-gnb-{self.harness.charm.app.name}"

        expected_calls = [
            call(relation_id=relation_id, gnb_name=expected_gnb_name, tac=default_tac_int),
            call(relation_id=relation_id, gnb_name=expected_gnb_name, tac=test_tac_int),
        ]
        self.harness.update_config(key_values={"tac": test_tac})
        self.mock_publish_gnb_identity.assert_has_calls(expected_calls)


    def test_given_fiveg_gnb_identity_relation_not_created_when_update_config_does_not_publish_gnb_identity(  # noqa: E501
        self,
    ):
        self.harness.update_config(key_values={"tac": "12345"})
        self.mock_publish_gnb_identity.assert_not_called()
