from fastapi import FastAPI
from .routes import logs
from .routes import anomalies


app = FastAPI(
    title="OpsGPT Backend",
    description="AI-powered Ops Co-Pilot",
    version="0.1.0"
)

app.include_router(logs.router)
app.include_router(anomalies.router)

@app.get("/")
def health_check():
    return {"status": "OpsGPT backend running"}
