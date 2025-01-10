# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import PropertyMock, patch

import pytest
from ops import testing

from charm import SdcoreGnbIntegratorCharm


class GnbIntegratorUnitTestFixtures:
    patcher_publish_gnb_information = patch("charm.FivegCoreGnbRequires.publish_gnb_information")
    patcher_gnb_core_remote_tac = patch(
        "charm.FivegCoreGnbRequires.tac", new_callable=PropertyMock
    )
    patcher_gnb_core_remote_plmns = patch(
        "charm.FivegCoreGnbRequires.plmns", new_callable=PropertyMock
    )

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.mock_publish_gnb_information = (
            GnbIntegratorUnitTestFixtures.patcher_publish_gnb_information.start()
        )
        self.mock_gnb_core_remote_tac = (
            GnbIntegratorUnitTestFixtures.patcher_gnb_core_remote_tac.start()
        )
        self.mock_gnb_core_remote_plmns = (
            GnbIntegratorUnitTestFixtures.patcher_gnb_core_remote_plmns.start()
        )
        yield
        request.addfinalizer(self.teardown)

    @staticmethod
    def teardown() -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = testing.Context(
            charm_type=SdcoreGnbIntegratorCharm,
        )
