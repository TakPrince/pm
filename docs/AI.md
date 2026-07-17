# AI Integration Contract

This document describes the AI prompt design, response contract, and validation schemas used in the Project Management MVP.

## Model Choice
*   **Model**: `openai/gpt-oss-120b` (via OpenRouter)
*   **Default Max Tokens**: `1000` (set to prevent credit checking issues while ensuring complete structured payloads)

## Endpoints

### 1. AI Connectivity Check
*   **Path**: `GET /api/ai/test`
*   **Purpose**: Smoke-test OpenRouter connectivity with a simple arithmetic calculation (`2+2`).
*   **Response**:
    ```json
    {
      "response": "4"
    }
    ```

### 2. AI Chat & Kanban Operations
*   **Path**: `POST /api/ai/chat`
*   **Purpose**: Submit user instructions (e.g. "Add a card to progress") alongside the current board state and chat history. Returns the AI's reply and any resulting board updates.
*   **Payload**:
    ```json
    {
      "username": "user",
      "message": "Add task 'Prototype dashboard' to Discovery",
      "history": [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "Hello! How can I help you today?"}
      ]
    }
    ```
*   **Response**:
    ```json
    {
      "reply": "I have added the task 'Prototype dashboard' to the Discovery column.",
      "board": {
        "columns": [
          {
            "id": "col-backlog",
            "title": "Backlog",
            "cardIds": ["card-1", "card-2"]
          },
          {
            "id": "col-discovery",
            "title": "Discovery",
            "cardIds": ["card-3", "card-abc123"]
          },
          ...
        ],
        "cards": {
          "card-1": { ... },
          "card-abc123": {
            "id": "card-abc123",
            "title": "Prototype dashboard",
            "details": "Details here"
          }
        }
      }
    }
    ```

---

## The System Prompt

The backend dynamically formats the following `SYSTEM_PROMPT` by injecting the user's active board state:

```text
You are a helpful Project Management Assistant for a Kanban board.
The Kanban board has 5 columns:
1. Backlog (id: "col-backlog")
2. Discovery (id: "col-discovery")
3. In Progress (id: "col-progress")
4. Review (id: "col-review")
5. Done (id: "col-done")

The user can ask you to create, edit, move, or delete cards.
Here is the current board data:
<SERIALIZED_CURRENT_BOARD_JSON>

Your response must be a single, valid JSON object with the following keys:
1. "reply": A friendly, concise response text explaining what you did or answering the user's question.
2. "board": If you made any changes to the board, provide the full updated board object (including columns and cards) matching the schema of the current board data. If you did NOT make any changes to the board, set "board" to null.

Rules for updates:
- Do NOT change the column IDs or column structure. You can only move card IDs between columns' "cardIds" lists, add new card IDs to "cardIds" and to the "cards" dictionary, edit card details/titles in the "cards" dictionary, or delete card IDs.
- For new cards, generate a unique ID starting with "card-" (e.g., "card-abc123").
- Ensure all card IDs in "cardIds" lists exist in the "cards" dictionary, and vice versa.
- Do NOT make up columns or change their order.
```

---

## Validation & Sanitization

To prevent LLM hallucinations from corrupting user data:
1.  **Pydantic Schema Check**: The returned `board` object is validated against the Pydantic `BoardData` model (verifying types, lists, and dicts).
2.  **Structural Integrity Check**: We enforce that column count (5), column IDs, and column order are identical to the pre-chat state. The AI cannot add, rename (outside of frontend user commands), or delete columns.
3.  **Referential Integrity Check**: We verify that all card IDs inside the columns' `cardIds` arrays exist in the `cards` dictionary, and that no orphaned card entries exist in the `cards` dictionary.
4.  **Transaction Safety**: If validation fails, the database transaction is rejected, the update is discarded, and a `400 Bad Request` is returned to the frontend.
