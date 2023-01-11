# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import unittest.mock as mock

import pytest
from ops.testing import Harness

from charm import SRIOVCNICharm


@pytest.fixture(autouse=True)
def lk_client():
    with mock.patch("ops.manifests.manifest.Client") as mock_lightkube:
        yield mock_lightkube.return_value


@pytest.fixture
def harness():
    harness = Harness(SRIOVCNICharm)
    try:
        harness.set_leader(True)
        yield harness
    finally:
        harness.cleanup()


@pytest.fixture
def charm(harness):
    harness.begin_with_initial_hooks()
    yield harness.charm
