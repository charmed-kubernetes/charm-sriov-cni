# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import logging
from typing import Dict

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


class SRIOVCNIManifests(Manifests):
    def __init__(self, charm, charm_config):
        manipulations = [ConfigRegistry(self), SetCNIPath(self)]

        super().__init__("sriov-cni", charm.model, "upstream/sriov-cni", manipulations)
        self.charm_config = charm_config

    @property
    def config(self) -> Dict:
        return dict(**self.charm_config)
