# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.


from ops import testing

from tests.unit.fixtures import GnbIntegratorUnitTestFixtures


class TestCharmConfigure(GnbIntegratorUnitTestFixtures):
    def test_given_core_gnb_relation_relation_when_configure_then_gnb_information_is_provided(
        self
    ):
        self.mock_gnb_core_remote_tac.return_value = 1
        self.mock_gnb_core_remote_plmns.return_value = None
        core_gnb_relation = testing.Relation(
            endpoint="fiveg_core_gnb", interface="fiveg_core_gnb"
        )
        state_in = testing.State(
            leader=True,
            relations=[core_gnb_relation],
            model=testing.Model(name="my-model"),
        )

        self.ctx.run(self.ctx.on.update_status(), state_in)

        self.mock_publish_gnb_information.assert_called_once_with(
            gnb_name="my-model-gnb-sdcore-gnb-integrator"
        )
