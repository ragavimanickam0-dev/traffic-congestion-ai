import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.routers import (
    auth,
    locations,
    weather,
    traffic,
    predictions,
    routes,
    reports,
    saved_locations,
    analytics
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TrafficIntel AI - Mobility & Congestion Intelligence API",
    description="Production-grade AI platform for urban traffic flow forecasting, route alternatives, and multi-horizon congestion prediction.",
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(weather.router, prefix="/api")
app.include_router(traffic.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(saved_locations.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

FRONTEND_DIR = PROJECT_ROOT / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{page_name}.html", include_in_schema=False)
    async def serve_page(page_name: str):
        page_file = FRONTEND_DIR / f"{page_name}.html"
        if page_file.exists():
            return FileResponse(page_file)
        return FileResponse(FRONTEND_DIR / "index.html")

    CSS_DIR = FRONTEND_DIR / "css"
    JS_DIR = FRONTEND_DIR / "js"
    if CSS_DIR.exists():
        app.mount("/css", StaticFiles(directory=str(CSS_DIR)), name="css")
    if JS_DIR.exists():
        app.mount("/js", StaticFiles(directory=str(JS_DIR)), name="js")

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "active_db": getattr(engine, "name", "sqlite")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
