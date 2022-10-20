# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import unittest.mock as mock

from manifests import SetCNIPath


def test_set_cni_path(harness):
    harness.disable_hooks()
    harness.begin_with_initial_hooks()
    harness.update_config({"cni-bin-dir": "/opt/cni/foo"})
    patch = SetCNIPath(harness.charm.manifests)
    volume = mock.MagicMock()
    volume.hostPath.path = "/opt/test"
    obj = mock.MagicMock()
    obj.spec.template.spec.volumes = [volume]
    patch(obj)

    assert obj.spec.template.spec.volumes[0].hostPath.path == "/opt/cni/foo"
