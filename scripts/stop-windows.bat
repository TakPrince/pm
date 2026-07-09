@echo off
set CONTAINER_NAME=pm-main
cd /d "%~dp0.."

docker stop %CONTAINER_NAME% >nul 2>nul
docker rm %CONTAINER_NAME% >nul 2>nul

echo Project Management MVP stopped
