# AI Project Builder

A full-stack application that turns a topic/specification into a source-code project, previews files, downloads a ZIP, and publishes to GitHub after OAuth authorization.

## Stack
- Frontend: React 18, Vite, JavaScript, CSS
- Backend: FastAPI, Python, HTTPX
- AI: configurable OpenAI-compatible Chat Completions endpoint
- GitHub: OAuth web flow and GitHub REST/Git Data APIs
- Upload parsing: pypdf, python-docx, optional Pillow + pytesseract

## Requirements
- Python 3.10+
- Node.js 18+
- An API key for your chosen OpenAI-compatible AI provider
- Optional GitHub OAuth App credentials for direct publishing
- Optional Tesseract OCR binary for image text extraction

## Run locally

### 1. Configure backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Edit `backend/.env` and set:
- `AI_API_KEY`: your AI provider key
- `AI_BASE_URL`: provider's OpenAI-compatible API base URL
- `AI_MODEL`: a model supported by that provider
- `APP_SECRET`: long random secret (e.g. `python -c "import secrets; print(secrets.token_urlsafe(48))"`)

Run the API from the `backend` directory:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Optional GitHub OAuth
Create a GitHub OAuth App in GitHub Developer Settings:
- Homepage URL: `http://localhost:5173`
- Authorization callback URL: `http://localhost:8000/api/github/callback`

Put the OAuth App client ID and secret into `backend/.env`. The app uses the `repo` OAuth scope so it can create private repositories and write to repositories owned by the connected user. This is broader than public-only publishing; use a GitHub App with fine-grained Contents and Metadata permissions for a production deployment if you need least privilege. Never put secrets in frontend environment variables.

Restart the backend after changing `.env`.

### 3. Run frontend
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`.

If your frontend is hosted elsewhere, set `VITE_API_BASE` before starting Vite and update `FRONTEND_URL` in backend `.env` to the exact frontend origin.

## Features
- Topic text entry and PDF/DOCX/TXT/Markdown/image uploads (image OCR requires Tesseract installed)
- Language and framework choices
- AI generation into a relative-path file map
- File tree and file content preview
- ZIP export with path checks and secret-file exclusions
- GitHub OAuth login, repository listing, create repository, publish to existing owned repositories
- Confirmation checkbox before publishing
- REST API errors shown in the UI

## API endpoints
- `GET /api/health`
- `POST /api/projects/analyze`
- `POST /api/projects/analyze-upload`
- `POST /api/projects/generate`
- `GET /api/projects/{project_id}/files`
- `GET /api/projects/{project_id}/download`
- `GET /api/github/status`
- `GET /api/github/login`
- `GET /api/github/callback`
- `GET /api/github/repositories`
- `POST /api/github/publish`

## Tests
From `backend/`:
```bash
pip install pytest
PYTHONPATH=. pytest
```
Health check: open `http://localhost:8000/api/health`.

## Security and production notes
- AI and GitHub secrets are backend-only. The frontend has no provider keys.
- Session cookie is HttpOnly via Starlette SessionMiddleware; use HTTPS and `COOKIE_SECURE=true` in production.
- OAuth state is validated and expires after 10 minutes.
- Projects are session-scoped and stored in server memory. Restarting the backend clears projects and OAuth session state; use Redis/DB for durable multi-worker deployment.
- For production, replace in-memory session/project stores with Redis or a database, add CSRF/origin protections for state-changing endpoints, apply rate limiting, enforce HTTPS, add request quotas and audit logs, and use a GitHub App with narrower permissions if practical.
- Generated code is untrusted output: review before running. This tool does not execute generated code.
- Existing-repository publishing uses Git Data API to create a commit on the selected branch. GitHub API permissions and repository branch protections may prevent publishing.
- If creating a brand-new empty repository, the first generated file is initialized via the Contents API; depending on GitHub initialization timing, retry may be needed. For best reliability, create a repository with README initialization or publish to an existing branch.
- Do not commit `.env` files or real credentials. `.env.example` should contain placeholders only.

## Troubleshooting
- `503 AI provider is not configured`: set `AI_API_KEY` in `backend/.env`.
- GitHub button says OAuth is not configured: set both GitHub OAuth values and check callback URL exactly matches.
- `401` after connecting: reconnect GitHub.
- OCR upload fails: install the Tesseract system binary and Python packages.
- AI provider returns an error: confirm the base URL, model name, key, and available quota.
