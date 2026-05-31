#!/usr/bin/env bash
set -e
NAME="mc-$(hostname)"
globus-compute-endpoint configure "$NAME"
cp /home/compute/user_config_template.yaml.j2 "$HOME/.globus_compute/$NAME/user_config_template.yaml.j2"
exec globus-compute-endpoint start "$NAME"
