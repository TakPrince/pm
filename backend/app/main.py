from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Project Management MVP")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "frontend" / "out"
FALLBACK_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


static_dir = STATIC_DIR if STATIC_DIR.exists() else FALLBACK_STATIC_DIR
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
