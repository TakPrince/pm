@echo off
set IMAGE_NAME=pm-main:latest
set CONTAINER_NAME=pm-main
set PORT=8000
cd /d "%~dp0.."

docker build -t %IMAGE_NAME% .
docker stop %CONTAINER_NAME% >nul 2>nul
docker rm %CONTAINER_NAME% >nul 2>nul

if exist .env (
  docker run --env-file .env -d --name %CONTAINER_NAME% -p %PORT%:8000 %IMAGE_NAME%
) else (
  docker run -d --name %CONTAINER_NAME% -p %PORT%:8000 %IMAGE_NAME%
)

echo Project Management MVP is running at http://localhost:%PORT%
