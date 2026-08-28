#!/bin/sh
HERE=$(dirname "$0")
. "$HERE/wandb_env.sh"
printf '{"Authorization": "Bearer %s"}' "$WANDB_API_KEY"
