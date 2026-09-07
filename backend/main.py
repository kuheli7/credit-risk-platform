"""NeoStats AI Credit Risk Intelligence Platform - FastAPI Backend."""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.routes.overview import router as overview_router
from backend.api.routes.eda import router as eda_router
from backend.api.routes.risk import router as risk_router
from backend.api.routes.rules import router as rules_router
from backend.api.routes.chat import router as chat_router
from src.utils.logger import logger

app = FastAPI(
    title="NeoStats Credit Risk Intelligence API",
    description="Enterprise Credit Scoring, Explainable AI (SHAP), Decision Rules, and NL-to-SQL Analytics API.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(overview_router)
app.include_router(eda_router)
app.include_router(risk_router)
app.include_router(rules_router)
app.include_router(chat_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "platform": "NeoStats Credit Risk Intelligence",
        "version": "1.0.0",
        "engine": "LightGBM + TreeSHAP + Groq Qwen"
    }

# Mount static frontend assets
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    @app.get("/")
    def serve_frontend_root():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Allow client-side routing to fallback to index.html if not an API or static path
        file_candidate = FRONTEND_DIR / full_path
        if file_candidate.exists() and file_candidate.is_file():
            return FileResponse(str(file_candidate))
        return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.on_event("startup")
async def startup_event():
    logger.info("NeoStats Credit Risk Platform FastAPI Server started.")
