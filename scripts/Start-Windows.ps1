$ImageName = "pm-main:latest"
$ContainerName = "pm-main"
$Port = "8000"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Set-Location $ProjectRoot

docker build -t $ImageName .
docker stop $ContainerName 2>$null | Out-Null
docker rm $ContainerName 2>$null | Out-Null

if (Test-Path ".env") {
    docker run --env-file .env -d --name $ContainerName -p "${Port}:8000" $ImageName
} else {
    docker run -d --name $ContainerName -p "${Port}:8000" $ImageName
}

Write-Host "Project Management MVP is running at http://localhost:$Port"
