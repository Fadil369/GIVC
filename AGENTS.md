# Repository Guidelines

## Project Structure & Module Organization
The FastAPI backend lives at the root with `fastapi_app.py` and domain modules in `auth/`, `services/`, `config/`, `pipeline/`, and `utils/`. The React + TypeScript UI sits in `frontend/src/` with feature folders such as `components/`, `hooks/`, and `services/`, and worker adapters deploy from `workers/`. Operational assets and documentation stay in `scripts/`, `analysis_data/`, and `docs/`, while tests mirror runtime structure across `tests/unit`, `tests/integration`, and `tests/test_auth`.

## Build, Test, and Development Commands
- `pnpm install` (fallback `npm install`) resolves frontend dependencies.
- `pnpm dev` launches the Vite dev server on http://localhost:3000 with `/api` proxied to the backend.
- `uvicorn fastapi_app:app --reload --port 8000` starts the FastAPI service.
- `pnpm build` outputs the production bundle to `dist/`; `pnpm preview` serves it for smoke checks.
- `docker-compose up -d postgres mongodb redis` provisions local data stores for integration runs.

## Coding Style & Naming Conventions
Format backend code with Black (100-character width) and isort; run `black . && isort .` before submitting changes. Keep functions and variables in `snake_case`, classes in `PascalCase`, and configuration constants uppercase snake. Frontend TypeScript follows ESLint + Prettier; `pnpm lint` and `pnpm format:check` enforce two-space indentation, PascalCase components, camelCase hooks, and shared types living in `frontend/src/types/`.

## Testing Guidelines
Vitest covers the UI—keep specs in `tests/unit` named `ComponentName.test.tsx` and run `pnpm test:coverage` to stay above 85% coverage. Pytest drives backend verification; mirror module paths such as `tests/test_auth/`, reuse fixtures from `tests/conftest.py`, and execute `pytest --cov=. --cov-report=term-missing` before a pull request.

## Commit & Pull Request Guidelines
Use Conventional Commits (`feat(claims): …`) on branches like `feature/*`, `bugfix/*`, or `hotfix/*` cut from `develop`. Ensure each commit passes local lint and test checks. Pull requests need a short summary, linked issues, validation checklist, and UI evidence when relevant; request maintainers listed in `CONTRIBUTING.md` and avoid force-push after review starts.

## Security & Configuration Tips
Base environment files on `.env.example` and keep secrets, certificates, and `logs/` out of Git—double-check with `git status`. Run `pnpm security:audit` ahead of releases and follow `PRE_PUSH_CHECKLIST.md` plus `SECURITY.md` when handling NPHIES credentials or PHI. Record new configuration requirements in `docs/DEPLOYMENT_GUIDE.md` and sync worker changes with `wrangler.toml` for reproducible deployments.
