# Frontend Instructions

## Current App

The frontend is a Next.js app using React, TypeScript, Tailwind CSS, and `@dnd-kit`. It is currently a frontend-only Kanban demo served by `src/app/page.tsx`, which renders `KanbanBoard`.

Current behavior:
- Five fixed Kanban columns are defined in `src/lib/kanban.ts`.
- Column titles can be renamed inline.
- Cards can be added and deleted.
- Cards can be moved and reordered with drag and drop.
- Board state is currently local React state and resets on refresh.

## Important Files

- `src/app/page.tsx`: app entry point for the board.
- `src/app/layout.tsx`: metadata and font setup.
- `src/app/globals.css`: Tailwind import, color variables, global styles.
- `src/components/KanbanBoard.tsx`: top-level client component and board state owner.
- `src/components/KanbanColumn.tsx`: column rendering, droppable area, rename input, card list, add form.
- `src/components/KanbanCard.tsx`: sortable card rendering and delete action.
- `src/components/NewCardForm.tsx`: local add-card form.
- `src/lib/kanban.ts`: board types, initial data, ID generation, and card movement logic.
- `src/lib/kanban.test.ts`: unit tests for movement logic.
- `src/components/KanbanBoard.test.tsx`: component tests for board behavior.
- `tests/kanban.spec.ts`: Playwright tests for browser workflows.

## Local Commands

- `npm run dev`: start the Next.js dev server.
- `npm run build`: build the frontend.
- `npm run lint`: run ESLint.
- `npm run test:unit`: run Vitest tests.
- `npm run test:e2e`: run Playwright tests.
- `npm run test:all`: run unit and Playwright tests.

## Conventions

- Keep components simple and focused.
- Prefer existing component boundaries before adding new abstractions.
- Keep Kanban board data compatible with `BoardData`, `Column`, and `Card` from `src/lib/kanban.ts` until the backend schema is approved.
- Use the root project color variables from `src/app/globals.css`.
- Preserve accessible names for inputs and buttons because tests rely on them.
- Use `data-testid` only where role or text selectors are not practical.
- Keep browser workflow tests in `tests/` and unit/component tests close to source under `src/`.

## Upcoming Integration Notes

- The frontend will later be statically built and served by FastAPI at `/`.
- Login will be added before the board is shown.
- Board state will later load from and save to the FastAPI backend.
- The AI chat sidebar will be added after backend persistence and AI routes exist.
