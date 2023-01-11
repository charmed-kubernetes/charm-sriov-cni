# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import logging
from typing import Dict

from lightkube.models.core_v1 import Toleration
from ops.manifests import ConfigRegistry, Manifests, Patch

log = logging.getLogger(__name__)


class SetCNIPath(Patch):
    """Change CNI path to install SRIOV-CNI plugin to"""

    def __call__(self, obj) -> None:
        volumes = obj.spec.template.spec.volumes
        if volumes:
            for v in volumes:
                if v.name == "cnibin":
                    v.hostPath.path = self.manifests.config["cni-bin-dir"]


class UpdateDaemonSetTolerations(Patch):
    """Update sriovdp's to also tolerate a noschedule control-plane."""

    def __call__(self, obj):
        """Update the DaemonSet object in the manifest."""
        if not (
            obj.kind == "DaemonSet" and obj.metadata.name.startswith("kube-sriov-cni")
        ):
            return

        current_keys = {
            toleration.key for toleration in obj.spec.template.spec.tolerations
        }
        control_plane_key = "node-role.kubernetes.io/control-plane"
        if control_plane_key not in current_keys:
            log.info(f"Adding tolerations to {obj.metadata.name}")
            obj.spec.template.spec.tolerations += [
                Toleration(
                    key=control_plane_key,
                    operator="Exists",
                    effect="NoSchedule",
                )
            ]


class SRIOVCNIManifests(Manifests):
    def __init__(self, charm, charm_config):
        manipulations = [
            ConfigRegistry(self),
            SetCNIPath(self),
            UpdateDaemonSetTolerations(self),
        ]

        super().__init__("sriov-cni", charm.model, "upstream/sriov-cni", manipulations)
        self.charm_config = charm_config

    @property
    def config(self) -> Dict:
        """Returns config mapped from charm config."""
        config = dict(**self.charm_config)

        for key, value in dict(**config).items():
            if value == "" or value is None:
                del config[key]

        config["release"] = config.pop("release", None)
        return config
