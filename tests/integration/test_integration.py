#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


import logging
from pathlib import Path

import pytest
import yaml

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
APP_NAME = METADATA["name"]
NMS_CHARM_NAME = "sdcore-nms-k8s"


@pytest.fixture(scope="module")
@pytest.mark.abort_on_fail
async def deploy(ops_test, request):
    """Deploy the charm-under-test."""
    charm = Path(request.config.getoption("--charm_path")).resolve()
    await ops_test.model.deploy(
        charm,
        application_name=APP_NAME,
    )
    await ops_test.model.deploy(
        NMS_CHARM_NAME,
        application_name=NMS_CHARM_NAME,
        channel="edge",
        trust=True,
    )


@pytest.mark.abort_on_fail
async def test_deploy_charm_and_wait_for_active_status(
    ops_test,
    deploy,
):
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        status="active",
        timeout=1000,
    )


@pytest.mark.abort_on_fail
async def test_relate_and_wait_for_active_status(
    ops_test,
    deploy,
):
    await ops_test.model.integrate(
        relation1=f"{APP_NAME}:fiveg_gnb_identity", relation2=NMS_CHARM_NAME
    )
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        raise_on_error=False,
        status="active",
        timeout=1000,
    )
