# Database Schema

This document describes the SQLite database schema for the Project Management MVP.

## Overview

- **Type:** SQLite (local file-based)
- **Location:** `./pm.db` (in the project root when running locally, or in a mounted volume in Docker)
- **Creation:** Automatic on first app startup if the database does not exist
- **Board Storage:** Kanban board data (columns, cards, ordering) is stored as JSON in a `data` column
- **Users:** Schema supports multiple users for future expansion; MVP uses hardcoded `user`

## Schema

### Users Table

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Stores user accounts. For the MVP, only one user (`user`) is seeded at startup.

### Boards Table

```sql
CREATE TABLE boards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL DEFAULT 'My Board',
  data TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, name)
);
```

Stores one or more boards per user. The MVP creates one default board per user.

- `user_id`: Foreign key to `users.id`
- `name`: Board name (e.g., "My Board")
- `data`: JSON-serialized board state (see schema below)
- `created_at`, `updated_at`: Timestamps for tracking

## Board Data JSON Schema

The `data` column in the `boards` table contains a JSON string matching the `BoardData` TypeScript type from the frontend:

```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-discovery",
      "title": "Discovery",
      "cardIds": ["card-3"]
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-4", "card-5"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": ["card-6"]
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": ["card-7", "card-8"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Align roadmap themes",
      "details": "Draft quarterly themes with impact statements and metrics."
    },
    "card-2": {
      "id": "card-2",
      "title": "Gather customer signals",
      "details": "Review support tags, sales notes, and churn feedback."
    },
    "card-3": {
      "id": "card-3",
      "title": "Prototype analytics view",
      "details": "Sketch initial dashboard layout and key drill-downs."
    },
    "card-4": {
      "id": "card-4",
      "title": "Refine status language",
      "details": "Standardize column labels and tone across the board."
    },
    "card-5": {
      "id": "card-5",
      "title": "Design card layout",
      "details": "Add hierarchy and spacing for scanning dense lists."
    },
    "card-6": {
      "id": "card-6",
      "title": "QA micro-interactions",
      "details": "Verify hover, focus, and loading states."
    },
    "card-7": {
      "id": "card-7",
      "title": "Ship marketing page",
      "details": "Final copy approved and asset pack delivered."
    },
    "card-8": {
      "id": "card-8",
      "title": "Close onboarding sprint",
      "details": "Document release notes and share internally."
    }
  }
}
```

### JSON Structure

- `columns`: Array of column objects in display order
  - `id`: Unique column identifier
  - `title`: User-editable column name
  - `cardIds`: Array of card IDs in this column, in order

- `cards`: Object mapping card IDs to card data
  - `id`: Unique card identifier
  - `title`: Card title
  - `details`: Card description or notes

## Initialization

On first startup, if the database does not exist:

1. Create `pm.db`
2. Create the `users` and `boards` tables
3. Insert the hardcoded MVP user (`username: "user"`)
4. Insert one default board for the user with the initial example data shown above

## Persistence

- Board updates (column renames, card moves, card create/delete) write the entire updated JSON to the `data` column
- The `updated_at` timestamp is automatically updated on each write
- The database persists across container restarts if the volume/file is mounted or preserved

## Future Expansion

When adding multi-user support:

- Remove the hardcoded user check in authentication
- Create a user on signup (with hashed password, to be added)
- Load the board for the authenticated user
- Allow users to create multiple boards
- The schema already supports these without changes
