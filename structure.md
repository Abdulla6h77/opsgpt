opsgpt/
│
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── config.py              # Env & settings
│   │   ├── routes/
│   │   │   ├── logs.py             # Upload + parse logs
│   │   │   ├── anomalies.py        # Anomaly detection API
│   │   │   └── explain.py          # LangChain explanation
│   │   ├── services/
│   │   │   ├── log_parser.py       # Log parsing + chunking
│   │   │   ├── anomaly_client.py   # Gradient inference client
│   │   │   └── llm_agent.py        # LangChain agent logic
│   │   ├── schemas/
│   │   │   └── log_schema.py
│   │   └── utils/
│   │       └── helpers.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai/
│   ├── training/
│   │   └── anomaly_training.ipynb  # Gradient GPU training
│   ├── inference/
│   │   └── anomaly_service.py      # Deployed model
│   └── models/
│       └── anomaly_model.pkl
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # Dashboard
│   │   ├── chat/
│   │   │   └── page.tsx            # OpsGPT chat
│   │   └── components/
│   │       ├── Timeline.tsx
│   │       ├── UploadLogs.tsx
│   │       └── HealthCard.tsx
│   ├── package.json
│   └── next.config.js
│
├── demo-data/
│   ├── sample_logs.log
│   └── log_generator.py
│
├── docs/
│   ├── architecture.png
│   └── problem_statement.md
│
├── README.md
├── LICENSE
└── .env.example