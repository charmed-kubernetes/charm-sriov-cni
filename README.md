# SR-IOV CNI Charm

[SR-IOV CNI plugin][sriov-cni] enables the configuration and usage of
SR-IOV VFs in Kubernetes.

This charm, when deployed to a Kubernetes cloud, will create a DaemonSet that
installs the SR-IOV CNI plugin on every Kubernetes node in the cluster.

This charm is a component of Charmed Kubernetes. For full information,
please visit the [official Charmed Kubernetes docs](https://ubuntu.com/kubernetes/docs/cni-sriov).

[sriov-cni]: https://github.com/k8snetworkplumbingwg/sriov-cni

## Development

### Building the charm

This charm can be built locally using [charmcraft][]

```
charmcraft pack
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
juju deploy ./sriov-cni.charm
```

## Contributing

If you wish to suggest changes to the code, docs or contribute to this charm, please
see the [CONTRIBUTING.md][] page.

[contributing.md]: ./CONTRIBUTING.md
[charmcraft]: https://github.com/canonical/charmcraft/
