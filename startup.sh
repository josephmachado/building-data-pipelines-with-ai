#!/bin/bash
set -e
cd /home/app

# Create the env in the mounted repo if it doesn't exist yet
if [ ! -f pyproject.toml ]; then
    uv init --bare --python 3.13
    uv add jupyterlab pyspark pyspark[sql] duckdb jupysql duckdb-engine \
        "grpcio-status>=1.48.1" "zstandard>=0.25.0" grpcio \
        googleapis-common-protos pyarrow toml mcp[cli]
fi

# Ensure deps are synced (in case pyproject exists but .venv doesn't)
uv sync

exec uv run jupyter lab --allow-root --ip=0.0.0.0 --no-browser --IdentityProvider.token=''
