#!/bin/bash
set -e

# Start Jupyter Lab in the foreground
exec uv run jupyter lab --allow-root --ip=0.0.0.0 --no-browser --IdentityProvider.token=''
