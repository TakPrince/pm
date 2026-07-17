from pathlib import Path
import tempfile

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.routing import Mount

from backend.app.main import STATIC_DIR, app, health, hello
from backend.app.database import init_db


def test_frontend_static_export_exists() -> None:
    index_html = STATIC_DIR / "index.html"

    assert index_html.exists()
    assert "Kanban Studio" in index_html.read_text(encoding="utf-8")


def test_health_route() -> None:
    assert health() == {"status": "ok"}


def test_hello_route() -> None:
    assert hello() == {"message": "Hello from FastAPI"}


def test_api_routes_are_registered() -> None:
    routes = {
        route.path
        for route in app.routes
        if isinstance(route, APIRoute)
    }

    assert "/api/health" in routes
    assert "/api/hello" in routes
    assert "/api/board" in routes


def test_frontend_is_mounted_at_root() -> None:
    mounts = {
        route.path
        for route in app.routes
        if isinstance(route, Mount)
    }

    assert "" in mounts


def test_static_assets_are_exported() -> None:
    next_dir = Path(STATIC_DIR / "_next")

    assert next_dir.exists()


def test_get_board_for_user() -> None:
    """Test the GET /api/board endpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        init_db(db_path)

        from backend.app import database

        original_db_path = database.DB_PATH
        database.DB_PATH = db_path

        try:
            client = TestClient(app)
            response = client.get("/api/board?username=user")

            assert response.status_code == 200
            board = response.json()
            assert "columns" in board
            assert "cards" in board
            assert len(board["columns"]) == 5
            assert len(board["cards"]) == 8
        finally:
            database.DB_PATH = original_db_path


def test_get_board_nonexistent_user() -> None:
    """Test the GET /api/board endpoint with a nonexistent user."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        init_db(db_path)

        from backend.app import database

        original_db_path = database.DB_PATH
        database.DB_PATH = db_path

        try:
            client = TestClient(app)
            response = client.get("/api/board?username=nonexistent")

            assert response.status_code == 404
        finally:
            database.DB_PATH = original_db_path


def test_update_board_for_user() -> None:
    """Test the PUT /api/board endpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        init_db(db_path)

        from backend.app import database

        original_db_path = database.DB_PATH
        database.DB_PATH = db_path

        try:
            client = TestClient(app)

            response = client.get("/api/board?username=user")
            board = response.json()

            board["columns"][0]["title"] = "Updated Backlog"

            response = client.put("/api/board?username=user", json=board)

            assert response.status_code == 200
            updated_board = response.json()
            assert updated_board["columns"][0]["title"] == "Updated Backlog"

            response = client.get("/api/board?username=user")
            fetched_board = response.json()
            assert fetched_board["columns"][0]["title"] == "Updated Backlog"
        finally:
            database.DB_PATH = original_db_path


def test_update_board_invalid_payload() -> None:
    """Test the PUT /api/board endpoint with invalid payload."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        init_db(db_path)

        from backend.app import database

        original_db_path = database.DB_PATH
        database.DB_PATH = db_path

        try:
            client = TestClient(app)

            response = client.put(
                "/api/board?username=user",
                json={"invalid": "data"},
            )

            assert response.status_code == 422
        finally:
            database.DB_PATH = original_db_path


def test_ai_test_route_mocked() -> None:
    """Test the /api/ai/test route with mocked OpenRouter client."""
    from unittest.mock import patch
    
    with patch("backend.app.main.query_openrouter") as mock_query:
        mock_query.return_value = "4"
        
        client = TestClient(app)
        response = client.get("/api/ai/test")
        
        assert response.status_code == 200
        assert response.json() == {"response": "4"}
        mock_query.assert_called_once()


def test_ai_test_route_live() -> None:
    """Test the /api/ai/test route live ONLY if OPENROUTER_API_KEY is present."""
    import os
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        # Skip if API key is not configured
        return
        
    client = TestClient(app)
    response = client.get("/api/ai/test")
    
    assert response.status_code == 200
    res_data = response.json()
    assert "response" in res_data
    # Clean the response and check if the result is correct
    ans = res_data["response"].strip()
    # The model could output "4" or "4." or "The answer is 4" etc.
    assert "4" in ans


def test_ai_chat_route_no_update_mocked() -> None:
    """Test POST /api/ai/chat route with no board changes returned."""
    from unittest.mock import patch
    from backend.app.database import get_board
    
    with patch("backend.app.main.process_ai_chat") as mock_process:
        mock_process.return_value = {"reply": "Greetings! I did not change the board.", "board": None}
        
        client = TestClient(app)
        payload = {"username": "user", "message": "hello", "history": []}
        response = client.post("/api/ai/chat", json=payload)
        
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["reply"] == "Greetings! I did not change the board."
        assert res_data["board"] is None
        mock_process.assert_called_once_with("hello", [], get_board("user"))


def test_ai_chat_route_with_update_mocked() -> None:
    """Test POST /api/ai/chat route applying and returning valid board updates."""
    from unittest.mock import patch
    import tempfile
    import json
    from backend.app.database import get_board
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        init_db(db_path)
        
        from backend.app import database
        original_db_path = database.DB_PATH
        database.DB_PATH = db_path
        
        try:
            current_board = get_board("user", db_path)
            # Create a clone of the board and simulate adding a card
            updated_board = json.loads(json.dumps(current_board))
            new_card_id = "card-new123"
            updated_board["cards"][new_card_id] = {
                "id": new_card_id,
                "title": "New AI Task",
                "details": "Details here"
            }
            updated_board["columns"][0]["cardIds"].append(new_card_id)
            
            with patch("backend.app.main.process_ai_chat") as mock_process:
                mock_process.return_value = {
                    "reply": "Added a new card for you.",
                    "board": updated_board
                }
                
                client = TestClient(app)
                payload = {
                    "username": "user",
                    "message": "add a card",
                    "history": [{"role": "user", "content": "hi"}]
                }
                response = client.post("/api/ai/chat", json=payload)
                
                assert response.status_code == 200
                res_data = response.json()
                assert res_data["reply"] == "Added a new card for you."
                assert res_data["board"] is not None
                assert new_card_id in res_data["board"]["cards"]
                
                # Check DB persistence
                db_board = get_board("user", db_path)
                assert new_card_id in db_board["cards"]
        finally:
            database.DB_PATH = original_db_path


def test_ai_chat_route_invalid_update_mocked() -> None:
    """Test POST /api/ai/chat route handling of invalid board schemas."""
    from unittest.mock import patch
    
    with patch("backend.app.main.process_ai_chat") as mock_process:
        # Simulate AI attempting to delete the columns key or structure
        mock_process.return_value = {
            "reply": "I broke the board.",
            "board": {"invalid": "schema"}
        }
        
        client = TestClient(app)
        payload = {"username": "user", "message": "break it", "history": []}
        response = client.post("/api/ai/chat", json=payload)
        
        assert response.status_code == 400
        assert "Invalid board update" in response.json()["detail"]

