"""
FastAPI Server for Homelab Mission Control Portal.
Serves REST APIs for system metrics and service control, real-time WebSocket log streams,
asset streaming, and the modern responsive Web Dashboard SPA.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from portal.supervisor import HomelabSupervisor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mission_control")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
OUTPUT_DIR = BASE_DIR / "output"

app = FastAPI(
    title="OmniForge Mission Control",
    description="Unified Web & Telegram Mini App Portal for Homelab Services & Antigravity Agents",
    version="1.0.0",
)

# Enable CORS for Telegram Mini App & remote clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supervisor = HomelabSupervisor()

# Ensure directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------
# REST APIs: System & Services
# ---------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Quick health probe."""
    return {"status": "ok", "app": "OmniForge Mission Control"}


@app.get("/api/system")
async def get_system():
    """Returns real-time CPU, RAM, Disk, and load metrics."""
    return supervisor.get_system_metrics()


@app.get("/api/services")
async def list_services():
    """Returns status of all monitored system services."""
    results = []
    for svc in supervisor.monitored_services:
        status = await supervisor.get_service_status(svc)
        results.append(status)
    return {"services": results}


@app.post("/api/services/{service_name}/{action}")
async def control_service(service_name: str, action: str):
    """Start, stop, or restart a managed system service."""
    if service_name not in supervisor.monitored_services:
        raise HTTPException(status_code=400, detail=f"Service '{service_name}' is not in the monitored allowlist.")
    result = await supervisor.control_service(service_name, action)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Service control failed"))
    return result


@app.get("/api/assets")
async def list_assets(limit: int = 30):
    """Lists recent audio stories, affirmations, and clips in output/."""
    assets = await supervisor.list_recent_assets(limit=limit)
    return {"assets": assets}


@app.get("/api/assets/{filename}")
async def get_asset(filename: str):
    """Serves a generated audio or media asset file with streaming support."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")

    suffix = file_path.suffix.lower()
    media_type = "audio/mpeg" if suffix == ".mp3" else "video/mp4" if suffix == ".mp4" else "application/octet-stream"
    return FileResponse(path=file_path, media_type=media_type, filename=filename)


@app.get("/api/cartridges")
async def get_cartridges():
    """Returns loaded OmniForge cartridges and capabilities."""
    cartridges_dir = BASE_DIR / "cartridges"
    found = []
    if cartridges_dir.exists():
        for f in cartridges_dir.glob("*.py"):
            if not f.name.startswith("__") and f.name != "base.py":
                found.append(f.stem)
    return {
        "cartridges": found,
        "total": len(found),
        "engine": "OmniForge V2 Deep Sleep & Autonomous Pipelines"
    }


# ---------------------------------------------------------
# WebSockets: Real-time Live Log Stream & Agent Dispatcher
# ---------------------------------------------------------

@app.websocket("/ws/logs/{service_name}")
async def websocket_logs(websocket: WebSocket, service_name: str):
    """Streams live service journalctl lines in real time to connected web clients."""
    await websocket.accept()
    logger.info(f"WebSocket client connected to logs for {service_name}")
    try:
        async for line in supervisor.stream_service_logs(service_name=service_name, lines=50):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from {service_name} logs")
    except Exception as e:
        logger.error(f"Error in log stream websocket: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


@app.websocket("/ws/agent")
async def websocket_agent_dispatch(websocket: WebSocket):
    """
    Receives prompt tasks from the web portal, spawns Antigravity CLI,
    and streams stdout and thoughts in real time.
    """
    await websocket.accept()
    logger.info("WebSocket client connected to Agent Dispatcher")
    try:
        while True:
            try:
                data = json.loads(data_str)
                prompt = data.get("prompt", "").strip()
                model = data.get("model", "gemini-3.8-flash-medium")
                effort = data.get("effort", "low")
            except Exception:
                prompt = data_str.strip()
                model = "gemini-3.8-flash-medium"
                effort = "low"

            if not prompt:
                await websocket.send_text("⚠️ Empty prompt received.")
                continue

            async for chunk in supervisor.run_agent_prompt(prompt, model=model, effort=effort):
                await websocket.send_text(chunk)
                await asyncio.sleep(0.005)

            await websocket.send_text("[[AGENT_RUN_COMPLETE]]")
    except WebSocketDisconnect:
        logger.info("Agent Dispatcher client disconnected")
    except Exception as e:
        logger.error(f"Error in agent dispatch websocket: {e}")


# ---------------------------------------------------------
# Static Frontend SPA
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/portal", response_class=HTMLResponse)
async def serve_portal():
    """Serves the main Mission Control single-page application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Mission Control Dashboard Initializing...</h1>", status_code=200)


def run_portal(host: str = "0.0.0.0", port: int = 8080):
    """Launches the Mission Control server via Uvicorn."""
    import uvicorn
    uvicorn.run("portal.server:app", host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    run_portal()
