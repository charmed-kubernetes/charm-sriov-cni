# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import unittest.mock as mock
from pathlib import Path
from typing import List, Tuple

import pytest

from manifests import SetCNIPath, UpdateDaemonSetTolerations


def test_update_tolerations(harness):
    harness.disable_hooks()
    harness.begin_with_initial_hooks()
    patch = UpdateDaemonSetTolerations(harness.charm.manifests)
    toleration = mock.MagicMock()
    toleration.key = "node-role.kubernetes.io/important"
    toleration.operator = "Exists"
    toleration.effect = "NoSchedule"

    obj = mock.MagicMock()
    obj.kind = "DaemonSet"
    obj.metadata.name = "kube-sriov-cni-ds-amd64"
    obj.spec.template.spec.tolerations = [toleration]
    patch(obj)
    assert len(obj.spec.template.spec.tolerations) == 2
    assert all(
        t.key.endswith(("control-plane", "important"))
        for t in obj.spec.template.spec.tolerations
    )


def test_update_tolerations_only_changes_recognized_daemonset(
    harness,
):
    harness.disable_hooks()
    harness.begin_with_initial_hooks()
    patch = UpdateDaemonSetTolerations(harness.charm.manifests)
    obj = mock.Mock(kind="DaemonSet", **{"metadata.name": "not-sriovdp"})
    patch(obj)
    # Mock object would raise a TypeError
    # if any attempt to access the spec is attempted


@pytest.mark.parametrize(
    "volumes,expected",
    [
        pytest.param(
            [("cnibin", "/opt/cni/bin"), ("testvolume", "/opt/test/path")],
            set([("cnibin", "/opt/cni/foo"), ("testvolume", "/opt/test/path")]),
        )
    ],
)
def test_set_cni_path(harness, volumes, expected):
    harness.disable_hooks()
    harness.begin_with_initial_hooks()
    harness.update_config({"cni-bin-dir": "/opt/cni/foo"})
    patch = SetCNIPath(harness.charm.manifests)
    obj = mock.MagicMock()
    obj.spec.template.spec.volumes = _mock_volume_factory(volumes)
    patch(obj)

    volumes = set((v.name, v.hostPath.path) for v in obj.spec.template.spec.volumes)

    assert volumes == expected


def _mock_volume_factory(args: List[Tuple[str, str]]):
    volumes = []
    for a in args:
        volume = mock.MagicMock()
        volume.name, volume.hostPath.path = a
        volumes.append(volume)

    return volumes


@pytest.mark.parametrize(
    "release",
    [
        None,
        *sorted(path.name for path in Path("upstream/sriov-cni/manifests").iterdir()),
    ],
)
def test_bundled_installer_preserves_upgrade_contract(harness, release):
    harness.disable_hooks()
    config = {"cni-bin-dir": "/custom/cni/bin"}
    if release:
        config["release"] = release
    harness.update_config(config)
    harness.begin()
    (resource,) = harness.charm.manifests.resources
    daemonset = resource.resource
    assert resource.name == "kube-sriov-cni-ds-amd64"
    assert resource.namespace == "kube-system"
    assert daemonset.spec.selector.matchLabels == {"name": "sriov-cni"}
    spec = daemonset.spec.template.spec
    assert spec.nodeSelector["kubernetes.io/arch"] == "amd64"
    (container,) = spec.containers
    assert container.image.startswith(
        "ghcr.io/canonical/cdk/k8snetworkplumbingwg/sriov-cni:v"
    )
    assert container.imagePullPolicy == "IfNotPresent"
    (volume,) = spec.volumes
    (mount,) = container.volumeMounts
    assert volume.name == mount.name == "cnibin"
    assert volume.hostPath.path == "/custom/cni/bin"
    assert mount.mountPath == "/host/opt/cni/bin"
    toleration_keys = [toleration.key for toleration in spec.tolerations]
    assert toleration_keys.count("node-role.kubernetes.io/control-plane") == 1
