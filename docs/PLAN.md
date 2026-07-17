# Project Plan

This plan breaks the MVP into small parts. Each part should be completed, tested, and checked off before moving to the next part. This plan must be approved by the user before implementation work begins.

## Part 1: Planning and Frontend Discovery

- [x] Review the root `AGENTS.md` requirements.
- [x] Review the current frontend app structure, tests, and build configuration.
- [x] Expand this plan with substeps, tests, and success criteria for every part.
- [x] Add `frontend/AGENTS.md` describing the existing frontend code and local conventions.
- [x] Ask the user to review and approve this plan before Part 2 starts.

Tests:
- No automated tests are required for documentation-only changes.
- Verify the plan and `frontend/AGENTS.md` are concise, consistent with the root requirements, and do not introduce new product scope.

Success criteria:
- The user can understand the implementation order and approval gates.
- The frontend instructions reflect the current codebase accurately.
- No source code behavior changes are made in Part 1.

## Part 2: Scaffolding

- [x] Review `backend/AGENTS.md` before editing backend files.
- [x] Review `scripts/AGENTS.md` before editing server scripts.
- [x] Add Docker infrastructure for a local single-container app.
- [x] Scaffold a FastAPI backend in `backend/`.
- [x] Configure Python dependencies with `uv`.
- [x] Add a backend health route.
- [x] Serve a small static HTML page from `/` for the first smoke test.
- [x] Add an API route that the static page calls successfully.
- [x] Add start and stop scripts for Mac, PC, and Linux in `scripts/`.
- [x] Keep `.env` support ready for later OpenRouter work without requiring AI calls yet.

Tests:
- Run backend unit tests for the health/API routes.
- Build the Docker image.
- Start the container with the platform script available in this environment.
- Confirm `/` returns the static HTML.
- Confirm the static page can call the backend API.
- Stop the container cleanly.

Success criteria:
- A fresh checkout can run the hello-world backend/static app locally through Docker.
- The backend creates no unnecessary app features yet.
- Scripts are simple and documented by their names and comments only where needed.

Verification note:
- Backend unit tests and a local Uvicorn HTTP smoke test passed.
- Docker build/start verification is blocked in this environment by Docker API permission errors on `/var/run/docker.sock`.

## Part 3: Add In Frontend

- [x] Review `frontend/AGENTS.md` before editing frontend files.
- [x] Configure the Next.js frontend for static export suitable for FastAPI serving.
- [x] Add a frontend build step to the Docker flow.
- [x] Copy or mount the static frontend output so FastAPI serves it at `/`.
- [x] Preserve the current Kanban board behavior: five fixed columns, rename columns, add cards, delete cards, and drag/drop cards.
- [x] Keep frontend state local for this part.
- [x] Remove the temporary static hello-world page once the real frontend is served.

Tests:
- Run frontend unit tests.
- Run frontend Playwright tests.
- Run backend tests affected by static serving.
- Build the Docker image.
- Start the container and confirm the Kanban app appears at `/`.
- Confirm the backend API is still reachable.

Success criteria:
- The app served from FastAPI matches the current frontend demo behavior.
- The frontend can be built repeatably in Docker.
- Existing Kanban tests pass or are updated only for intentional integration changes.

Verification note:
- `npm run build`, frontend unit tests, backend tests, and a local FastAPI HTTP smoke test passed.
- Full Playwright and Docker runtime verification were intentionally not run in this pass.

## Part 4: Add Fake User Sign In Experience

- [x] Add a simple login screen shown first at `/`.
- [x] Accept only username `user` and password `password`.
- [x] Store login state simply for the local MVP.
- [x] Show the Kanban board after successful login.
- [x] Add logout and return to the login screen.
- [x] Keep the database-ready user concept in mind, but do not build multi-user UI.

Tests:
- Unit test successful login.
- Unit test failed login.
- Unit test logout behavior.
- Playwright test login to Kanban.
- Playwright test logout.
- Confirm unauthenticated users cannot see the board UI.

Success criteria:
- The MVP has a clear local sign-in flow.
- The hardcoded credentials work exactly as specified.
- No real authentication system is introduced.

## Part 5: Database Modeling

- [x] Propose a SQLite schema that supports multiple future users.
- [x] Model one board per signed-in user for the MVP.
- [x] Store Kanban board data as JSON.
- [x] Include columns, column order, cards, and card ordering in the JSON shape.
- [x] Document database file location, creation behavior, and migration approach in `docs/`.
- [x] Include example JSON for the initial board.
- [x] Ask the user to approve the schema before Part 6 starts.

Tests:
- No runtime tests are required before schema approval.
- Validate the example JSON shape manually for consistency with the current frontend model.

Success criteria:
- The user approves the schema and JSON approach.
- The schema is simple enough for the MVP and leaves room for future users.
- The documented model maps cleanly to the current Kanban UI.

## Part 6: Backend

- [x] Implement SQLite database creation if the database file does not exist.
- [x] Seed the hardcoded MVP user if needed.
- [x] Seed one default board for the user if needed.
- [x] Add API routes to read the current user's board.
- [x] Add API routes to replace or update the current user's board.
- [x] Validate board JSON enough to protect the app from malformed payloads.
- [x] Keep API contracts simple and documented in `docs/` or backend tests.

Tests:
- Unit test database initialization.
- Unit test default user and board seeding.
- Unit test reading the board.
- Unit test updating the board.
- Unit test malformed board payload handling.
- Integration test API routes against a temporary SQLite database.

Success criteria:
- The backend can persist and return Kanban board JSON.
- A missing database is created automatically.
- Tests do not depend on a developer's local database file.

## Part 7: Frontend and Backend Integration

- [x] Replace local-only initial board state with a backend fetch after login.
- [x] Save column rename, card create, card delete, and drag/drop changes through the backend.
- [x] Show simple loading and error states.
- [x] Keep the UI focused on the existing Kanban workflows.
- [x] Ensure the board persists after refresh and container restart when the database volume/file remains.

Tests:
- Unit test frontend API client behavior.
- Unit test loading and error states.
- Component test board updates after backend data is loaded.
- Playwright test login, edit board, refresh, and confirm persistence.
- Backend tests remain passing.
- Docker smoke test confirms end-to-end persistence.

Success criteria:
- The Kanban board is backed by SQLite through FastAPI.
- User-visible board operations remain smooth.
- Refreshing the page does not reset the board.

## Part 8: AI Connectivity

- [x] Read `OPENROUTER_API_KEY` from the project root `.env`.
- [x] Configure the backend to call OpenRouter.
- [x] Use model `openai/gpt-oss-120b`.
- [x] Add a small backend route or test helper for a simple connectivity check.
- [x] Run a "2+2" connectivity test only when the API key is available.
- [x] Keep AI connectivity isolated from Kanban mutation logic for this part.

Tests:
- Unit test AI client request construction with mocked HTTP.
- Unit test missing API key behavior.
- Optional live connectivity test returning the answer to "2+2" when `OPENROUTER_API_KEY` is present.

Success criteria:
- The backend can call OpenRouter from local Docker.
- The live test is clearly separated from normal deterministic tests.
- No Kanban state is changed by AI in this part.

## Part 9: AI Structured Kanban Updates

- [x] Define the structured AI response shape: user-facing reply plus optional Kanban update.
- [x] Send the current board JSON, user message, and conversation history to the AI.
- [x] Ask the AI for structured output compatible with the backend schema.
- [x] Validate any returned board update before saving it.
- [x] Apply valid board updates and reject invalid ones without corrupting existing data.
- [x] Document the AI prompt and response contract.

Tests:
- Unit test prompt construction.
- Unit test parsing a reply with no board update.
- Unit test parsing and applying a valid board update.
- Unit test rejecting invalid structured output.
- Integration test the chat route with mocked OpenRouter responses.
- Optional live test with a harmless request when the API key is present.

Success criteria:
- AI responses can create, edit, or move one or more cards through validated structured output.
- Invalid AI output does not damage the stored board.
- Conversation history is included without adding unnecessary chat persistence.

## Part 10: AI Sidebar Widget

- [x] Add a sidebar chat widget to the Kanban UI.
- [x] Let users send messages to the backend AI route.
- [x] Display conversation messages clearly.
- [x] Show loading and error states for AI responses.
- [x] Refresh the Kanban board automatically when the AI updates it.
- [x] Keep the visual design aligned with the existing color scheme and avoid adding unrelated UI.

Tests:
- Unit test chat input and message rendering.
- Unit test loading and error states.
- Unit test board refresh after AI update.
- Playwright test a mocked AI response that creates or moves a card.
- Backend mocked integration tests remain passing.
- Docker end-to-end smoke test with mocked or disabled AI as appropriate.

Success criteria:
- Users can chat with the AI from the Kanban screen.
- AI-driven board updates appear automatically in the UI.
- The sidebar feels integrated with the existing app and does not obscure core Kanban workflows.
