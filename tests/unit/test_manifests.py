# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import unittest.mock as mock
from typing import List, Tuple

import pytest

from manifests import SetCNIPath


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
        (volume.name, volume.hostPath.path) = a
        volumes.append(volume)

    return volumes
