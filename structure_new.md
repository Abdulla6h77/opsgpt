opsgpt/
|-- .cursor/
|-- .git/
|-- .qodo/
|-- ai/
|   |-- explain.py
|   |-- incident.py
|   |-- remediation.py
|   |-- severity.py
|   |-- inference/
|   |   `-- anomaly_service.py
|   |-- models/
|   |   |-- anomaly_model.pkl
|   |   `-- service_encoder.pkl
|   `-- training/
|       `-- anomaly_training.ipynb
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- configs.py
|   |   |-- main.py
|   |   |-- core/
|   |   |   |-- __init__.py
|   |   |   |-- config.py
|   |   |   |-- database.py
|   |   |   |-- logging.py
|   |   |   |-- rate_limit.py
|   |   |   `-- security.py
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- anomaly.py
|   |   |   |-- incident.py
|   |   |   `-- log_batch.py
|   |   |-- routes/
|   |   |   |-- __init__.py
|   |   |   |-- anomalies.py
|   |   |   |-- debug.py
|   |   |   |-- explain.py
|   |   |   |-- incidents.py
|   |   |   `-- logs.py
|   |   |-- schemas/
|   |   |   |-- __init__.py
|   |   |   |-- anomaly.py
|   |   |   |-- common.py
|   |   |   |-- debug.py
|   |   |   |-- health.py
|   |   |   |-- incident.py
|   |   |   |-- log_batch.py
|   |   |   |-- log_schema.py
|   |   |   `-- logs.py
|   |   |-- services/
|   |   |   |-- __init__.py
|   |   |   |-- anomaly_client.py
|   |   |   |-- llm_agent.py
|   |   |   |-- llm_incident_analyzer.py
|   |   |   `-- log_parser.py
|   |   `-- utils/
|   |       |-- __init__.py
|   |       `-- helpers.py
|   |-- services/
|   |   |-- __init__.py
|   |   `-- llm_incident_analyzer.py
|   `-- dockerfile
|-- demo_data/
|   |-- log_generator.py
|   `-- sample_logs.log
|-- dev/
|   |-- Include/
|   |-- Lib/
|   |-- Scripts/
|   |-- share/
|   `-- pyvenv.cfg
|-- frontend/
|   |-- .next/ (build output)
|   |-- app/
|   |   |-- api/
|   |   |   |-- anomalies/
|   |   |   |   |-- detect/
|   |   |   |   |   `-- route.ts
|   |   |   |   `-- route.ts
|   |   |   |-- incidents/
|   |   |   |   |-- [id]/
|   |   |   |   |   `-- route.ts
|   |   |   |   `-- route.ts
|   |   |   `-- logs/
|   |   |       `-- upload/
|   |   |           `-- route.ts
|   |   |-- chat/
|   |   |   `-- page.tsx
|   |   |-- components/
|   |   |   |-- HealthCard.tsx
|   |   |   |-- Timeline.tsx
|   |   |   `-- UploadLogs.tsx
|   |   |-- dashboard/
|   |   |   `-- page.tsx
|   |   |-- incidents/
|   |   |   |-- [id]/
|   |   |   |   `-- page.tsx
|   |   |   `-- page.tsx
|   |   |-- upload/
|   |   |   `-- page.tsx
|   |   |-- [id]/
|   |   |   `-- page.tsx
|   |   |-- layout.tsx
|   |   `-- page.tsx
|   |-- components/
|   |   |-- charts/
|   |   |   |-- incidents-chart.tsx
|   |   |   `-- severity-chart.tsx
|   |   |-- ui/
|   |   |   |-- alert.tsx
|   |   |   |-- badge.tsx
|   |   |   |-- button.tsx
|   |   |   |-- card.tsx
|   |   |   `-- table.tsx
|   |   |-- anomaly-list.tsx
|   |   |-- incident-table.tsx
|   |   |-- metric-card.tsx
|   |   |-- navbar.tsx
|   |   |-- remediation-list.tsx
|   |   `-- sidebar.tsx
|   |-- lib/
|   |   |-- api.ts
|   |   |-- server-api.ts
|   |   `-- types.ts
|   |-- node_modules/
|   |-- styles/
|   |   `-- globals.css
|   |-- .env.example
|   |-- next-env.d.ts
|   |-- next.config.js
|   |-- package-lock.json
|   |-- package.json
|   |-- postcss.config.js
|   |-- tailwind.config.ts
|   `-- tsconfig.json
|-- .env
|-- .gitignore
|-- CODEBASE_INDEX.md
|-- README.md
|-- requirements.txt
|-- run_tests.ps1
`-- structure.md
