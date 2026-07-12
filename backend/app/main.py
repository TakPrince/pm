from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from backend.app.database import init_db, get_board, update_board
from backend.app.models import BoardData

app = FastAPI(title="Project Management MVP")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "frontend" / "out"
FALLBACK_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.get("/api/board")
def get_board_route(username: str) -> BoardData:
    """Fetch the board for the authenticated user."""
    try:
        board_data = get_board(username)
        return BoardData(**board_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/api/board")
def update_board_route(username: str, board: BoardData) -> BoardData:
    """Update the board for the authenticated user."""
    try:
        board_dict = board.model_dump()
        updated = update_board(username, board_dict)
        return BoardData(**updated)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


static_dir = STATIC_DIR if STATIC_DIR.exists() else FALLBACK_STATIC_DIR
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
