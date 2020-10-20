# SR-IOV CNI Charm

This is an early proof-of-concept charm for deploying and managing Intel's
[SR-IOV CNI plugin](https://github.com/intel/sriov-cni) via Juju.

## Development

### Building the charm

This charm can be built locally using [charmcraft][]

```
charmcraft build
```

### Building the resources

In order to test the sriov-cni charm, you must first build the container image
(note: this requires Docker):

```
cd image
./build
```

### Testing

Deploy Charmed Kubernetes with storage support.

Add k8s to Juju controller:

```
juju scp kubernetes-master/0:config ~/.kube/config
juju add-k8s my-k8s-cloud --controller $(juju switch | cut -d: -f1)
```

Create k8s model:

```
juju add-model my-k8s-model my-k8s-cloud
```

Deploy the SR-IOV Network Device Plugin:

```
juju deploy ./sriov-cni.charm --resource sriov-cni-image=sriov-cni
```
