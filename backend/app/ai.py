import os
import json
from pathlib import Path
import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

MODEL_NAME = "openai/gpt-oss-120b"


class AIError(Exception):
    """Custom exception for AI connectivity and query errors."""
    pass


def query_openrouter(messages: list[dict], model: str = MODEL_NAME, max_tokens: int = 1000) -> str:
    """Send a chat completion request to the OpenRouter API."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise AIError("OPENROUTER_API_KEY environment variable is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/TakPrince/pm",
        "X-Title": "Project Management MVP",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    url = "https://openrouter.ai/api/v1/chat/completions"

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=30.0)
            
            if response.status_code != 200:
                raise AIError(f"OpenRouter API returned status {response.status_code}: {response.text}")
                
            data = response.json()
            content = data["choices"][0]["message"].get("content")
            if content is None:
                raise AIError("OpenRouter returned an empty message content (possibly due to safety filters or generation failure)")
            return content
            
    except httpx.RequestError as e:
        raise AIError(f"Network error communicating with OpenRouter: {str(e)}") from e
    except (KeyError, IndexError) as e:
        raise AIError(f"Unexpected response structure from OpenRouter: {response.text}") from e


SYSTEM_PROMPT = """You are a helpful Project Management Assistant for a Kanban board.
The Kanban board has 5 columns:
1. Backlog (id: "col-backlog")
2. Discovery (id: "col-discovery")
3. In Progress (id: "col-progress")
4. Review (id: "col-review")
5. Done (id: "col-done")

The user can ask you to create, edit, move, or delete cards.
Here is the current board data:
{board_json}

Your response must be a single, valid JSON object with the following keys:
1. "reply": A friendly, concise response text explaining what you did or answering the user's question.
2. "board": If you made any changes to the board, provide the full updated board object (including columns and cards) matching the schema of the current board data. If you did NOT make any changes to the board, set "board" to null.

Style & Formatting Rules for the "reply" field:
- Keep the response extremely brief, clean, and direct.
- Avoid verbose greetings, long explanations, or repetitive concluding lines.
- By default, provide a short 1-to-3 sentence answer unless the user explicitly requests a longer explanation or in-depth analysis.
- Do NOT use any markdown formatting elements (such as bold asterisks `**`, headers `#`, backticks, or lists) in your response. Output only plain, natural, classic paragraph text.
- For board mutations (creating, editing, moving, deleting), simply state what you did in one plain sentence (e.g. "I've added 'Write API docs' to the Backlog column.").

Rules for board updates:
- Do NOT change the column IDs or column structure. You can only move card IDs between columns' "cardIds" lists, add new card IDs to "cardIds" and to the "cards" dictionary, edit card details/titles in the "cards" dictionary, or delete card IDs.
- For new cards, generate a unique ID starting with "card-" (e.g., "card-abc123").
- Ensure every card object in the "cards" dictionary contains all three required fields: "id" (must match the dictionary key/ID), "title" (string), and "details" (string).
- When creating or editing cards, keep card "title" very short (2-5 words) and "details" extremely brief (1-2 sentences maximum). Do NOT write long paragraphs, lists, or multi-day schedules inside card details.
- Ensure all card IDs in "cardIds" lists exist in the "cards" dictionary, and vice versa.
- Do NOT make up columns or change their order.
"""


def process_ai_chat(user_message: str, history: list[dict], board_data: dict) -> dict:
    """Format prompt, send to OpenRouter, and parse JSON response structure."""
    system_prompt = SYSTEM_PROMPT.format(board_json=json.dumps(board_data, indent=2))
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_message})
    
    raw_response = query_openrouter(messages, max_tokens=4000)
    
    try:
        parsed = json.loads(raw_response)
        if "reply" not in parsed:
            raise AIError("AI response is missing the required 'reply' field")
        return parsed
    except json.JSONDecodeError as e:
        # Check if the model wrapped the JSON in markdown blocks
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            try:
                parsed = json.loads(cleaned)
                if "reply" not in parsed:
                    raise AIError("AI response is missing the required 'reply' field")
                return parsed
            except json.JSONDecodeError:
                pass
                
        # Attempt to extract 'reply' string using regex if JSON is truncated
        import re
        reply_match = re.search(r'"reply"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_response)
        if reply_match:
            reply_str = reply_match.group(1)
            try:
                reply_str = json.loads(f'"{reply_str}"')
            except Exception:
                pass
            return {
                "reply": f"{reply_str}\n\n(Note: The visual board could not be updated because the details generated by the AI were too long. Please try again with a shorter request.)",
                "board": None
            }
            
        raise AIError("The AI assistant's response was truncated or invalid because the text was too long. Please try again with a shorter or simpler request.") from e


def validate_and_sanitize_board_update(current_board: dict, updated_board: dict) -> dict:
    """Validate that the AI's updated board schema matches our business constraints."""
    # Pre-sanitize / heal missing card fields (id, details, title) to prevent Pydantic validation failures
    if isinstance(updated_board, dict) and "cards" in updated_board and isinstance(updated_board["cards"], dict):
        for card_id, card in updated_board["cards"].items():
            if isinstance(card, dict):
                if "id" not in card or not card["id"]:
                    card["id"] = card_id
                if "details" not in card:
                    card["details"] = ""
                if "title" not in card or not card["title"]:
                    card["title"] = "Untitled Task"

    from backend.app.models import BoardData
    try:
        validated = BoardData(**updated_board)
    except Exception as e:
        raise ValueError(f"AI board structure does not match Pydantic model: {str(e)}")

    # Check columns size and IDs
    expected_col_ids = [col["id"] for col in current_board["columns"]]
    actual_col_ids = [col.id for col in validated.columns]
    
    if expected_col_ids != actual_col_ids:
        raise ValueError(f"AI altered the column IDs or column order. Expected {expected_col_ids}, got {actual_col_ids}")

    # Check card list consistency
    card_ids_in_columns = set()
    for col in validated.columns:
        for cid in col.cardIds:
            if cid not in validated.cards:
                raise ValueError(f"Card ID '{cid}' is referenced in column '{col.id}' but does not exist in the cards dictionary")
            card_ids_in_columns.add(cid)
            
    for cid in validated.cards:
        if cid not in card_ids_in_columns:
            raise ValueError(f"Card ID '{cid}' exists in the cards dictionary but is not assigned to any column")

    return validated.model_dump()

