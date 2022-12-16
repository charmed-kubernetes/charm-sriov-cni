#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.manifests import Collector, ManifestClientError
from ops.model import ActiveStatus, MaintenanceStatus, WaitingStatus

from manifests import SRIOVCNIManifests

log = logging.getLogger(__name__)


class SRIOVCNICharm(CharmBase):
    """A Juju charm for SR-IOV CNI"""

    stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.manifests = SRIOVCNIManifests(self, self.config)
        self.collector = Collector(self.manifests)
        self.framework.observe(self.on.install, self._install_or_upgrade)
        self.framework.observe(self.on.upgrade_charm, self._install_or_upgrade)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

        self.framework.observe(self.on.list_versions_action, self._list_versions)
        self.framework.observe(self.on.list_resources_action, self._list_resources)
        self.framework.observe(self.on.scrub_resources_action, self._scrub_resources)
        self.framework.observe(self.on.sync_resources_action, self._sync_resources)
        self.framework.observe(self.on.update_status, self._update_status)

        self.stored.set_default(deployed=False)

    def _list_versions(self, event):
        self.collector.list_versions(event)

    def _list_resources(self, event):
        manifests = ""
        resources = event.params.get("resources", "")
        return self.collector.list_resources(event, manifests, resources)

    def _scrub_resources(self, event):
        manifests = ""
        resources = event.params.get("resources", "")
        return self.collector.scrub_resources(event, manifests, resources)

    def _sync_resources(self, event):
        manifests = ""
        resources = event.params.get("resources", "")
        try:
            self.collector.apply_missing_resources(event, manifests, resources)
        except ManifestClientError:
            msg = "Failed to apply missing resources. API Server unavailable."
            event.set_results({"result": msg})

    def _install_or_upgrade(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus("Ready")
            return
        self.unit.status = MaintenanceStatus("Applying SR-IOV CNI resources")
        log.info("Applying SRIOV-CNI manifests.")
        try:
            self.manifests.apply_manifests()
        except ManifestClientError:
            self.unit.status = WaitingStatus("Waiting for kube-apiserver")
            event.defer()
            return
        self.stored.deployed = True
        self._update_status(event)

    def _on_config_changed(self, event):
        self.unit.status = MaintenanceStatus("Applying SR-IOV CNI resources")
        try:
            self.manifests.apply_manifests()
        except ManifestClientError:
            self.unit.status = WaitingStatus("Waiting for kube-apiserver")
            event.defer()
            return
        self._update_status(event)

    def _update_status(self, _):
        if not self.stored.deployed:
            return

        unready = self.collector.unready

        if unready:
            self.unit.status = WaitingStatus(", ".join(unready))
        else:
            self.unit.set_workload_version(self.collector.short_version)
            self.unit.status = ActiveStatus("Ready")
            self.app.status = ActiveStatus(self.collector.long_version)


if __name__ == "__main__":
    main(SRIOVCNICharm)  # pragma: no cover
