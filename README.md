# SR-IOV CNI Charm

This is an early proof-of-concept charm for deploying and managing Intel's
[SR-IOV CNI plugin](https://github.com/intel/sriov-cni) via Juju.

## Development

### Building the image

Make sure you have docker installed. Then:

```
cd image
./build
```

### Building the charm

Install [Charmcraft](https://pypi.org/project/charmcraft/).

Build the charm:

```
charmcraft build
```

### Uploading to the charm store

In order to test the sriov-cni charm, you must first host the container image
somewhere it will be accessible from your Kubernetes cluster. The easiest way
to do this is to upload the charm to the charm store and attach the image as a
charm resource.

```
mkdir temp
cd temp
unzip ../sriov-cni.charm
charm push . cs:~${NAMESPACE}/sriov-cni
charm attach cs:~${NAMESPACE}/sriov-cni --channel unpublished sriov-cni-image=sriov-cni
charm release cs:~${NAMESPACE}/sriov-cni-0 --channel edge --resource sriov-cni-image-0
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
juju deploy cs:~${NAMESPACE}/sriov-cni --channel edge
```
