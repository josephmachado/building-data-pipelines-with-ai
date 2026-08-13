#!/bin/bash

set -euxo pipefail
cd /home/app
uv run python /home/app/generate_data.py
sleep 60
uv run python /home/app/run_ddl.py