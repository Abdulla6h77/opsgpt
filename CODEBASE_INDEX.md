# Codebase Index

Generated: 2026-03-10
Scope: First-party source only (`dev/`, `__pycache__/`, and compiled artifacts excluded).

## High-Level Layout

- `backend/`: FastAPI API, DB models, services, and route handlers.
- `ai/`: Rule-based enrichment logic + trained anomaly model assets.
- `frontend/`: Next.js app scaffold (currently mostly empty placeholders).
- `demo_data/`: Sample logs and synthetic log generator.
- Root docs/scripts: `README.md`, `project_context.md`, `structure.md`, `run_tests.ps1`, `requirements.txt`.

## Backend Index (`backend/app`)

- `main.py`: FastAPI app entrypoint, middleware, exception handling, router registration, startup DB init.
- `core/config.py`: Env loading and validation (`DATABASE_URL`, `API_KEY`, CORS, LLM settings).
- `core/database.py`: SQLAlchemy async engine/session setup and schema initialization.
- `core/security.py`: API key validation middleware helper.
- `core/logging.py`: Logging configuration.

- `routes/logs.py`:
  - `POST /logs/upload`: upload `.log`, parse, return log count.
- `routes/anomalies.py`:
  - `POST /anomalies/detect`: parse logs, run anomaly model, enrich (severity/explanation/remediation), persist incident + anomalies.
  - `GET /anomalies`: paginated anomaly listing with filters.
- `routes/incidents.py`:
  - `GET /incidents`: paginated incident listing with filters.
- `routes/debug.py`:
  - `POST /debug/test-db`: internal write test endpoint.
- `routes/explain.py`: present but empty.

- `services/log_parser.py`: Parses line-wise literal log dicts into `LogEntry` schema.
- `services/anomaly_client.py`: Loads `ai/models/*.pkl` and runs anomaly detection.
- `services/llm_incident_analyzer.py`: Optional LLM enrichment with JSON-safe fallback.
- `services/llm_agent.py`: present; not wired in active routes.

- `models/incident.py`: Incident ORM model.
- `models/anomaly.py`: Anomaly ORM model.
- `models/log_batch.py`: Uploaded log batch ORM model.

- `schemas/`: Pydantic request/response contracts (`anomaly.py`, `incident.py`, `logs.py`, etc.).
- `utils/helpers.py`: shared utility helpers.
- `configs.py`: present (legacy/unused in current app wiring).

## AI Index (`ai/`)

- `explain.py`: rule-based anomaly explanation generator.
- `severity.py`: anomaly severity scoring.
- `remediation.py`: root cause + suggested fix heuristics.
- `incident.py`: report + summary generation from anomaly list.
- `inference/anomaly_service.py`: present but empty.
- `training/anomaly_training.ipynb`: model training notebook.
- `models/anomaly_model.pkl`, `models/service_encoder.pkl`: serialized model artifacts used by backend.

## Frontend Index (`frontend/`)

- `app/page.tsx`: file exists but near-empty.
- `app/chat/page.tsx`: empty.
- `app/components/UploadLogs.tsx`: empty.
- `app/components/Timeline.tsx`: empty.
- `app/components/HealthCard.tsx`: empty.
- `package.json`, `next.config.js`: empty.

## Other Important Files

- `demo_data/sample_logs.log`: example logs for manual testing.
- `demo_data/log_generator.py`: synthetic log generator.
- `backend/services/llm_incident_analyzer.py`: duplicate top-level backend service module (outside `backend/app`).
- `backend/dockerfile`: container build file.

## Current State Notes

- Backend is the primary implemented surface.
- Frontend is scaffolded but not implemented yet.
- There are duplicate/legacy paths (`backend/services/`, `backend/app/configs.py`) that may need cleanup.
