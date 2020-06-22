#!/usr/bin/env bash
set -eu

echo "Copying CNI plugins"
cp -rv /opt/cni/bin/* /dest

echo "Sleeping forever"
while true; do sleep 86400; done
