# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import unittest.mock as mock
from pathlib import Path

import ops.testing
import pytest
from ops.model import ActiveStatus, WaitingStatus

ops.testing.SIMULATE_CAN_CONNECT = True

# Effective release of the charm revision before the schema default was set.
PREVIOUS_DEFAULT_RELEASE = "v2.6.3"


def _applied_image_tags(lk_client):
    daemonsets = [
        call.args[0]
        for call in lk_client.apply.call_args_list
        if call.args[0].kind == "DaemonSet"
    ]
    assert daemonsets, "no DaemonSet was applied"
    return {
        container.image.rsplit(":", 1)[1]
        for daemonset in daemonsets
        for container in daemonset.spec.template.spec.containers
    }


def test_refresh_with_release_unset_rolls_out_schema_default(harness, lk_client):
    harness.update_config({"release": PREVIOUS_DEFAULT_RELEASE})
    harness.begin_with_initial_hooks()
    assert _applied_image_tags(lk_client) == {PREVIOUS_DEFAULT_RELEASE}

    # juju refresh to this revision: the operator never set `release`, so the
    # unit now sees the new schema default; upgrade-charm then config-changed.
    with harness.hooks_disabled():
        harness.update_config(unset={"release"})
    lk_client.apply.reset_mock()
    harness.charm.on.upgrade_charm.emit()
    schema_default = harness.model.config["release"]
    assert schema_default != PREVIOUS_DEFAULT_RELEASE
    assert _applied_image_tags(lk_client) == {schema_default}

    lk_client.apply.reset_mock()
    harness.charm.on.config_changed.emit()
    assert _applied_image_tags(lk_client) == {schema_default}


def test_release_schema_default_matches_manifest_version_file(harness):
    harness.begin()
    version = Path("upstream/sriov-cni/version").read_text().strip()
    assert harness.model.config["release"] == version
    assert harness.charm.manifests.current_release == version


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
