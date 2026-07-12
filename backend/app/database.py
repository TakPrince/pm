import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "pm.db"

DEFAULT_BOARD_DATA = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {
            "id": "col-progress",
            "title": "In Progress",
            "cardIds": ["card-4", "card-5"],
        },
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}


def init_db(db_path: Path = DB_PATH) -> None:
    """Initialize the database with schema and seed data if it does not exist."""
    if db_path.exists():
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT 'My Board',
            data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, name)
        )
        """
    )

    cursor.execute("INSERT INTO users (username) VALUES (?)", ("user",))
    user_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO boards (user_id, name, data) VALUES (?, ?, ?)",
        (user_id, "My Board", json.dumps(DEFAULT_BOARD_DATA)),
    )

    conn.commit()
    conn.close()


def get_board(username: str, db_path: Path = DB_PATH) -> dict:
    """Fetch the board data for a given username."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT b.data FROM boards b
        JOIN users u ON b.user_id = u.id
        WHERE u.username = ?
        LIMIT 1
        """,
        (username,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"No board found for user: {username}")

    return json.loads(row[0])


def update_board(username: str, board_data: dict, db_path: Path = DB_PATH) -> dict:
    """Update the board data for a given username."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE boards SET data = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = (SELECT id FROM users WHERE username = ?)
        """,
        (json.dumps(board_data), username),
    )

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_affected == 0:
        raise ValueError(f"No board found for user: {username}")

    return board_data
