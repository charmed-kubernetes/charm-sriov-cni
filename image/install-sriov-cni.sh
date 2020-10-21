#!/usr/bin/env bash
set -eu

echo "Copying CNI plugins to host"
cp -rv /opt/cni/bin/* /dest

echo "Sleeping forever"
while true; do sleep 86400; done
