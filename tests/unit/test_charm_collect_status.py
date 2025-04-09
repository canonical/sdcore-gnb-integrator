# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


import pytest
from charms.sdcore_nms_k8s.v0.fiveg_core_gnb import PLMNConfig
from ops import ActiveStatus, BlockedStatus, WaitingStatus, testing

from tests.unit.fixtures import GnbIntegratorUnitTestFixtures


class TestCharmCollectUnitStatus(GnbIntegratorUnitTestFixtures):
    def test_fiveg_core_gnb_relation_not_created_when_collect_unit_status_then_status_is_blocked(
        self
    ):
        self.mock_gnb_core_remote_tac.return_value = 2
        self.mock_gnb_core_remote_plmns.return_value = [PLMNConfig(mcc="001", mnc="01", sst=1)]
        state_in = testing.State(leader=True)

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus(
            "Waiting for fiveg_core_gnb relation to be created"
        )

    @pytest.mark.parametrize(
        "tac,plmns",
        [
            pytest.param(None, [PLMNConfig(mcc="001", mnc="01", sst=31)], id="tac_is_none"),
            pytest.param(23, None, id="plmns_is_none"),
            pytest.param(None, None, id="plmns_and_tac_are_none"),
        ],
    )
    def test_fiveg_core_gnb_tac_and_plmns_unavailable_when_collect_unit_status_then_status_is_waiting(  # noqa: E501
        self, tac, plmns
    ):
        self.mock_gnb_core_remote_tac.return_value = tac
        self.mock_gnb_core_remote_plmns.return_value = plmns
        core_gnb_relation = testing.Relation(
                endpoint="fiveg_core_gnb", interface="fiveg_core_gnb"
            )
        state_in = testing.State(leader=True, relations=[core_gnb_relation])

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for TAC and PLMNs configuration")

    def test_fiveg_core_gnb_gnb_name_unavailable_when_collect_unit_status_then_status_is_blocked(  # noqa: E501
        self,
    ):
        self.mock_gnb_core_remote_tac.return_value = 1
        self.mock_gnb_core_remote_plmns.return_value = PLMNConfig(mcc="001", mnc="01", sst=31)
        core_gnb_relation = testing.Relation(
                endpoint="fiveg_core_gnb", interface="fiveg_core_gnb"
            )
        state_in = testing.State(leader=True, relations=[core_gnb_relation])

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == BlockedStatus(
            "Invalid configuration: gNB name is missing from the relation"
        )

    @pytest.mark.parametrize(
        "tac,plmns",
        [
            pytest.param(1, [PLMNConfig(mcc="001", mnc="01", sst=31)], id="single_plmn"),
            pytest.param(2, [PLMNConfig(mcc="001", mnc="01", sst=31), PLMNConfig(mcc="999", mnc="99", sst=12)], id="multiple_plmns"),  # noqa: E501
        ],
    )
    def test_pre_requisites_met_when_collect_unit_status_then_status_is_active(self, tac, plmns):
        self.mock_gnb_core_remote_tac.return_value = tac
        self.mock_gnb_core_remote_plmns.return_value = plmns
        core_gnb_relation = testing.Relation(
            endpoint="fiveg_core_gnb",
            interface="fiveg_core_gnb",
            local_app_data={"gnb-name": "gnb-integrator"},
        )
        state_in = testing.State(leader=True, relations=[core_gnb_relation])

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == ActiveStatus(
            f"PLMNs: {','.join([str(plmn.asdict()) for plmn in plmns])}, TAC: {tac}"
        )
