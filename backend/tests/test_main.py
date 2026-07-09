from pathlib import Path

from fastapi.routing import APIRoute
from starlette.routing import Mount

from backend.app.main import STATIC_DIR, app, health, hello


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
