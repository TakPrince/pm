# Scripts Instructions

This folder contains start and stop scripts for running the local Docker container.

## Current Scripts

- `start-linux.sh`: build and start the Docker container on Linux.
- `stop-linux.sh`: stop and remove the Docker container on Linux.
- `start-mac.sh`: build and start the Docker container on macOS.
- `stop-mac.sh`: stop and remove the Docker container on macOS.
- `start-windows.bat`: build and start the Docker container from Windows Command Prompt.
- `stop-windows.bat`: stop and remove the Docker container from Windows Command Prompt.
- `Start-Windows.ps1`: build and start the Docker container from PowerShell.
- `Stop-Windows.ps1`: stop and remove the Docker container from PowerShell.

## Conventions

- Keep scripts simple.
- Use image name `pm-main:latest`.
- Use container name `pm-main`.
- Serve the app on host port `8000`.
