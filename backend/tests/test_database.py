import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from backend.app.database import (
    DB_PATH,
    DEFAULT_BOARD_DATA,
    init_db,
    get_board,
    update_board,
)
from backend.app.models import BoardData


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        init_db(db_path)
        yield db_path


def test_init_db_creates_database(temp_db):
    """Test that init_db creates the database file."""
    assert temp_db.exists()


def test_init_db_creates_tables(temp_db):
    """Test that init_db creates users and boards tables."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "users" in tables
    assert "boards" in tables


def test_init_db_seeds_default_user(temp_db):
    """Test that init_db creates the default user."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username = 'user'")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "user"


def test_init_db_seeds_default_board(temp_db):
    """Test that init_db creates a default board for the user."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT data FROM boards b
        JOIN users u ON b.user_id = u.id
        WHERE u.username = 'user'
        """
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    board_data = json.loads(row[0])
    assert "columns" in board_data
    assert "cards" in board_data
    assert len(board_data["columns"]) == 5
    assert len(board_data["cards"]) == 8


def test_get_board(temp_db):
    """Test reading the board for a user."""
    board = get_board("user", temp_db)

    assert board == DEFAULT_BOARD_DATA
    assert len(board["columns"]) == 5
    assert len(board["cards"]) == 8


def test_get_board_nonexistent_user(temp_db):
    """Test that reading a board for a nonexistent user raises an error."""
    with pytest.raises(ValueError, match="No board found"):
        get_board("nonexistent", temp_db)


def test_update_board(temp_db):
    """Test updating the board for a user."""
    board = get_board("user", temp_db)

    board["columns"][0]["title"] = "Updated Backlog"
    updated = update_board("user", board, temp_db)

    assert updated["columns"][0]["title"] == "Updated Backlog"

    fetched = get_board("user", temp_db)
    assert fetched["columns"][0]["title"] == "Updated Backlog"


def test_update_board_nonexistent_user(temp_db):
    """Test that updating a board for a nonexistent user raises an error."""
    with pytest.raises(ValueError, match="No board found"):
        update_board("nonexistent", DEFAULT_BOARD_DATA, temp_db)


def test_board_data_validation():
    """Test that BoardData validates correctly."""
    board = BoardData(**DEFAULT_BOARD_DATA)

    assert len(board.columns) == 5
    assert len(board.cards) == 8
    assert board.columns[0].title == "Backlog"


def test_board_data_invalid_structure():
    """Test that BoardData rejects invalid structure."""
    invalid_board = {"columns": [], "cards": {}, "extra_field": "invalid"}

    board = BoardData(**invalid_board)
    assert board.columns == []
    assert board.cards == {}
