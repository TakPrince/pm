# Backend Instructions

The backend is a FastAPI app. It serves the static Next.js export from `/` and exposes API routes under `/api`.

## Current Files

- `app/main.py`: FastAPI application, static frontend mount, and API routes.
- `tests/test_main.py`: backend tests for the static frontend export and API routes.

## Conventions

- Keep backend code simple and explicit.
- Put app code under `backend/app/`.
- Put backend tests under `backend/tests/`.
- Keep API routes under `/api`.
- Do not add database, authentication, or AI behavior until the planned parts for those features.
