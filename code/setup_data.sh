#!/bin/bash

set -euxo pipefail
cd /home/app
uv run python /home/app/generate_data.py
uv run python /home/app/run_ddl.py