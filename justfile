# List available commands
default:
    just --list

# Docker compose up
up:
    docker compose up -d --build

# Docker compose down
down:
    docker compose down -v

sh:
  docker exec -ti sde-ai-tutorial bash

nb:
  open http://localhost:8888

airflow:
  open http://localhost:8080

# Restart docker containers
restart:
  just down 
  just up

# Start devcontainer
dev-up:
    devcontainer up --workspace-folder . --config .devcontainer/nvim/devcontainer.json

# Stop devcontainer
dev-down:
    devcontainer down --workspace-folder . --config .devcontainer/nvim/devcontainer.json

# Open nvim inside container, run as uv if you have setup uv python libraries
nvim *args:
    just dev-up
    devcontainer exec --workspace-folder . --config .devcontainer/nvim/devcontainer.json uv run nvim {{args}}
