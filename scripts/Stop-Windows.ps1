$ContainerName = "pm-main"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Set-Location $ProjectRoot

docker stop $ContainerName 2>$null | Out-Null
docker rm $ContainerName 2>$null | Out-Null

Write-Host "Project Management MVP stopped"
