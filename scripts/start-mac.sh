#!/usr/bin/env sh
set -eu

IMAGE_NAME="pm-main:latest"
CONTAINER_NAME="pm-main"
PORT="8000"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

docker build -t "$IMAGE_NAME" .
docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

# Ensure local pm.db file exists on the host so Docker doesn't mount it as a directory
touch pm.db

if [ -f .env ]; then
  docker run --env-file .env -v "$(pwd)/pm.db:/app/pm.db" -d --name "$CONTAINER_NAME" -p "$PORT:8000" "$IMAGE_NAME"
else
  docker run -v "$(pwd)/pm.db:/app/pm.db" -d --name "$CONTAINER_NAME" -p "$PORT:8000" "$IMAGE_NAME"
fi

echo "Project Management MVP is running at http://localhost:$PORT"
