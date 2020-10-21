FROM ubuntu:20.04
COPY sriov-cni/build/sriov /opt/cni/bin/sriov
COPY install-sriov-cni.sh /install-sriov-cni.sh
ENTRYPOINT ["/install-sriov-cni.sh"]
