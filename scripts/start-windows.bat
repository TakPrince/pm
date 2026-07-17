@echo off
set IMAGE_NAME=pm-main:latest
set CONTAINER_NAME=pm-main
set PORT=8000
cd /d "%~dp0.."

docker build -t %IMAGE_NAME% .
docker stop %CONTAINER_NAME% >nul 2>nul
docker rm %CONTAINER_NAME% >nul 2>nul

if not exist pm.db type NUL > pm.db

if exist .env (
  docker run --env-file .env -v "%cd%\pm.db:/app/pm.db" -d --name %CONTAINER_NAME% -p %PORT%:8000 %IMAGE_NAME%
) else (
  docker run -v "%cd%\pm.db:/app/pm.db" -d --name %CONTAINER_NAME% -p %PORT%:8000 %IMAGE_NAME%
)

echo Project Management MVP is running at http://localhost:%PORT%
