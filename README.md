# SR-IOV CNI Charm

[SR-IOV CNI plugin][sriov-cni] enables the configuration and usage of
SR-IOV VFs in Kubernetes.

This charm, when deployed to a Kubernetes cloud, will create a DaemonSet that
installs the SR-IOV CNI plugin on every Kubernetes node in the cluster.

This charm is a component of Charmed Kubernetes. For full information,
please visit the [official Charmed Kubernetes docs](https://ubuntu.com/kubernetes/docs/cni-sriov).

[sriov-cni]: https://github.com/k8snetworkplumbingwg/sriov-cni

## Bundled releases

The default release is **v2.10.0**. The charm also bundles v2.6.3, v2.7.0,
v2.8.1 and v2.9.0; select a bundled version with the `release` configuration.
The `cni-bin-dir` and `image-registry` settings continue to control the host
installation path and image mirror. The installer remains amd64-only and keeps
its existing DaemonSet name when upgrading.

The [v2.10.0 upstream documentation][upstream-support] describes deployment on
Kubernetes **1.16+**, and its installer uses the stable `apps/v1` API. This is
the basis for selecting v2.10.0 for CK 1.36, not a claim that upstream certified
Kubernetes 1.36 or that real VF allocation has been tested by this charm's unit
tests. Validate fresh installation and upgrades on CK 1.36 with SR-IOV hardware,
the SR-IOV device plugin, Multus, and a consuming workload before release.

[upstream-support]: https://github.com/k8snetworkplumbingwg/sriov-cni/blob/v2.10.0/README.md#kubernetes-quick-start

To regenerate selected stable releases (requires PyYAML):

```bash
python3 upstream/update.py --version v2.7.0 v2.8.1 v2.9.0 v2.10.0
python3 upstream/update.py --check --version v2.7.0 v2.8.1 v2.9.0 v2.10.0
```

The updater imports upstream's released Kubernetes 1.16+ DaemonSet, pins the
image to that release, and retains the deployed DaemonSet name and amd64 node
selector to avoid concurrent old and new installers. Other upstream settings,
including security hardening, are retained. Update `config.yaml` and
`upstream/sriov-cni/version` together when selecting a new default.

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
