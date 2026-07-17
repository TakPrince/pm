from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app.database import init_db, get_board, update_board
from backend.app.models import BoardData
from backend.app.ai import (
    query_openrouter,
    AIError,
    process_ai_chat,
    validate_and_sanitize_board_update,
)

app = FastAPI(title="Project Management MVP")

# Add CORS middleware to support local frontend development on different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/ai/test")
def test_ai_connectivity() -> dict[str, str]:
    """Test AI connectivity by calling OpenRouter to solve '2+2'."""
    try:
        messages = [{"role": "user", "content": "What is 2+2? Respond with just the answer number."}]
        response = query_openrouter(messages)
        return {"response": response.strip()}
    except AIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatPayload(BaseModel):
    username: str
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    board: BoardData | None = None


@app.post("/api/ai/chat", response_model=ChatResponse)
def ai_chat_route(payload: ChatPayload) -> ChatResponse:
    """Handle AI chat query and execute optional Kanban board updates."""
    try:
        current_board_dict = get_board(payload.username)
        
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in payload.history]
        ai_result = process_ai_chat(payload.message, history_dicts, current_board_dict)
        
        reply = ai_result["reply"]
        updated_board = ai_result.get("board")
        
        validated_board = None
        if updated_board is not None:
            sanitized_board = validate_and_sanitize_board_update(current_board_dict, updated_board)
            update_board(payload.username, sanitized_board)
            validated_board = BoardData(**sanitized_board)
            
        return ChatResponse(reply=reply, board=validated_board)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid board update: {str(e)}")
    except AIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
