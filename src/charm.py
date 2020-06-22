#!/usr/bin/env python3

import logging
from oci_image import OCIImageResource, OCIImageResourceError
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus


log = logging.getLogger()


class SRIOVCNICharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.image = OCIImageResource(self, 'sriov-cni-image')
        self.framework.observe(self.on.install, self.set_pod_spec)
        self.framework.observe(self.on.upgrade_charm, self.set_pod_spec)
        self.framework.observe(self.on.config_changed, self.set_pod_spec)

    def set_pod_spec(self, event):
        if not self.model.unit.is_leader():
            log.info('Not a leader, skipping set_pod_spec')
            self.model.unit.status = ActiveStatus()
            return

        try:
            image_details = self.image.fetch()
        except OCIImageResourceError as e:
            self.model.unit.status = e.status
            return

        cni_bin_dir = self.model.config.get('cni-bin-dir', '/opt/cni/bin')

        self.model.unit.status = MaintenanceStatus('Setting pod spec')
        self.model.pod.set_spec({
            'version': 3,
            'containers': [{
                'name': 'sriov-cni',
                'imageDetails': image_details,
                'volumeConfig': [{
                    'name': 'cni-bin',
                    'mountPath': '/dest',
                    'hostPath': {
                        'path': cni_bin_dir
                    }
                }]
            }],
            'kubernetesResources': {
                'pod': {
                    'hostNetwork': True,
                }
            }
        })
        self.model.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(SRIOVCNICharm)
