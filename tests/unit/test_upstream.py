# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
from pathlib import Path

import pytest
import yaml

from upstream.update import render_manifest, source_url, stable_version


@pytest.mark.parametrize("version", ["latest", "v2.10", "v2.10.0-rc.1", "../v2.10.0"])
def test_reject_mutable_or_nonstable_versions(version):
    with pytest.raises(argparse.ArgumentTypeError):
        stable_version(version)


@pytest.mark.parametrize(
    "version,directory",
    [("v2.7.0", "images/k8s-v1.16"), ("v2.8.1", "images")],
)
def test_manifest_source_layout(version, directory):
    assert source_url(version).endswith(f"/{version}/{directory}/sriov-cni-daemonset.yaml")


def test_render_preserves_installer_contract():
    source = Path(
        "upstream/sriov-cni/manifests/v2.6.3/sriov-cni-daemonset.yaml"
    ).read_text()
    upstream = yaml.safe_load(source)
    # Model the upstream resource rename and removal of amd64-only scheduling.
    upstream["metadata"]["name"] = "kube-sriov-cni-ds"
    upstream["spec"]["template"]["spec"].pop("nodeSelector")
    rendered = yaml.safe_load(render_manifest(yaml.safe_dump(upstream), "v2.10.0"))
    original = yaml.safe_load(source)
    assert rendered["metadata"] == original["metadata"]
    assert rendered["spec"]["selector"] == original["spec"]["selector"]
    spec = rendered["spec"]["template"]["spec"]
    original_spec = original["spec"]["template"]["spec"]
    assert spec["nodeSelector"] == original_spec["nodeSelector"]
    assert spec["volumes"] == original_spec["volumes"]
    container = spec["containers"][0]
    assert container["image"] == "ghcr.io/k8snetworkplumbingwg/sriov-cni:v2.10.0"
    container.pop("image")
    original_spec["containers"][0].pop("image")
    assert spec == original_spec
