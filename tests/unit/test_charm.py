# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import unittest.mock as mock

import ops.testing
import pytest
from ops.model import ActiveStatus, WaitingStatus

ops.testing.SIMULATE_CAN_CONNECT = True


@mock.patch("charm.SRIOVCNIManifests.apply_manifests")
@pytest.mark.parametrize("leader", [True, False])
def test_install_or_upgrade(mock_apply, harness, leader):
    harness.set_leader(leader)
    harness.disable_hooks()
    harness.begin()
    harness.charm._install_or_upgrade("mock_event")
    if leader:
        mock_apply.assert_called_once()
        assert harness.charm.stored.deployed
    else:
        assert isinstance(harness.charm.unit.status, ActiveStatus)


@pytest.mark.parametrize("deployed", [True, False])
@pytest.mark.parametrize("unready", ["Waiting", ""])
def test_update_status(harness, deployed, unready):
    with mock.patch(
        "charm.Collector.unready", new_callable=mock.PropertyMock, return_value=unready
    ):
        harness.set_leader()
        harness.begin_with_initial_hooks()
        charm = harness.charm
        charm.stored.deployed = deployed
        charm._update_status("mock-event")
        if deployed:
            if unready:
                assert isinstance(charm.unit.status, WaitingStatus)
            else:
                assert isinstance(charm.unit.status, ActiveStatus)
