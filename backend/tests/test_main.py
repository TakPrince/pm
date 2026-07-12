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
