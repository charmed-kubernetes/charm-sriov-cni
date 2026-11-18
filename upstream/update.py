#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
"""Import explicitly selected stable SR-IOV CNI release manifests."""

import argparse
import re
from pathlib import Path
from urllib.request import urlopen

import yaml

ROOT = Path(__file__).resolve().parent / "sriov-cni" / "manifests"
IMAGE = "ghcr.io/k8snetworkplumbingwg/sriov-cni"


def stable_version(value):
    """Accept only complete stable tags, never moving branches or image tags."""
    if not re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise argparse.ArgumentTypeError("expected a stable vMAJOR.MINOR.PATCH tag")
    return value


def source_url(version):
    """The Kubernetes 1.16+ manifest moved in the upstream 2.8 release."""
    parts = tuple(int(part) for part in version[1:].split("."))
    directory = "images/k8s-v1.16" if parts < (2, 8, 0) else "images"
    return (
        "https://raw.githubusercontent.com/k8snetworkplumbingwg/sriov-cni/"
        f"{version}/{directory}/sriov-cni-daemonset.yaml"
    )


def render_manifest(content, version):
    """Preserve the deployed resource identity and pin the released image."""
    manifest = yaml.safe_load(content)
    if manifest["kind"] != "DaemonSet" or manifest["apiVersion"] != "apps/v1":
        raise ValueError("expected the upstream apps/v1 installer DaemonSet")
    # Renaming this resource would leave the old installer running on upgrade.
    manifest["metadata"]["name"] = "kube-sriov-cni-ds-amd64"
    spec = manifest["spec"]["template"]["spec"]
    spec.setdefault("nodeSelector", {})["kubernetes.io/arch"] = "amd64"
    (container,) = spec["containers"]
    if container["name"] != "kube-sriov-cni":
        raise ValueError("unrecognized upstream installer container")
    container["image"] = f"{IMAGE}:{version}"
    return f"# Source: {source_url(version)}\n" + yaml.safe_dump(
        manifest, sort_keys=False, explicit_start=True
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", nargs="+", type=stable_version, required=True)
    parser.add_argument(
        "--check", action="store_true", help="compare generated content without writing"
    )
    args = parser.parse_args()
    mismatches = []
    for version in args.version:
        url = source_url(version)
        with urlopen(url, timeout=60) as response:
            rendered = render_manifest(response.read().decode("utf-8"), version)
        target = ROOT / version / "sriov-cni-daemonset.yaml"
        if target.exists() and target.read_text(encoding="utf-8") == rendered:
            print(f"Unchanged {version}: {url}")
        elif args.check:
            mismatches.append(str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
            print(f"Generated {version}: {url}")
    if mismatches:
        parser.exit(1, "Generated manifests differ: " + ", ".join(mismatches) + "\n")


if __name__ == "__main__":
    main()
