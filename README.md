# Project Management MVP

A collaborative Kanban board featuring an integrated AI project assistant. 

## Features

- **Interactive Kanban Board**: Drag and drop cards between five columns: Backlog, Discovery, In Progress, Review, and Done.
- **AI Assistant**: A collapsible floating chatbot widget that creates, edits, or moves cards on the board based on plain-text requests.
- **Persistent SQLite Storage**: Board state is saved locally to an SQLite database file.
- **Responsive Layout**: Designed for mobile and desktop screens with horizontal column scrolling and hover card expansion.

## Tech Stack

- **Frontend**: Next.js (TypeScript, TailwindCSS, React Dnd-kit)
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **AI Provider**: OpenRouter API (openai/gpt-oss-120b)
- **Package Manager**: UV (Python), NPM (Node.js)
- **Deployment**: Docker container

## Prerequisites

- Docker installed
- An OpenRouter API Key

## Setup and Running

1. Create a `.env` file in the project root directory:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

2. Start the application:
   - On Linux:
     ```bash
     ./scripts/start-linux.sh
     ```
   - On macOS:
     ```bash
     ./scripts/start-mac.sh
     ```
   - On Windows:
     ```cmd
     scripts\start-windows.bat
     ```

3. Open your browser and navigate to `http://localhost:8000`.

4. Log in with the default credentials:
   - **Username**: `user`
   - **Password**: `password`

5. To stop the application:
   - On Linux/macOS:
     ```bash
     ./scripts/stop-linux.sh
     ```

## Development and Testing

### Backend Tests
Ensure Python is installed and execute the Pytest suite:
```bash
python3 -m pytest
```

### Frontend Tests
Ensure Node.js is installed and execute Vitest:
```bash
npm --prefix frontend run test:unit
```
