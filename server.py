
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio
import random
import time

app = FastAPI(title="AVIATOR")

BASE = Path(__file__).parent

# Support both root and templates folder
if (BASE / "templates" / "index.html").exists():
    INDEX_FILE = BASE / "templates" / "index.html"
else:
    INDEX_FILE = BASE / "index.html"

# Static folder is optional
STATIC_DIR = BASE / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    if not INDEX_FILE.exists():
        return HTMLResponse("AVIATOR index.html not found", status_code=404)

    return INDEX_FILE.read_text(encoding="utf-8")


@app.get("/api/status")
async def status():
    return {
        "game": "AVIATOR",
        "mode": "virtual credits",
        "status": "online"
    }


@app.websocket("/ws")
async def game_socket(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            crash_at = round(random.uniform(1.2, 12), 2)

            await ws.send_json({
                "type": "waiting",
                "seconds": 5
            })

            await asyncio.sleep(5)
            start = time.monotonic()

            await ws.send_json({"type": "started"})

            while True:
                elapsed = time.monotonic() - start
                multiplier = round(1 + elapsed * 0.22, 2)

                if multiplier >= crash_at:
                    await ws.send_json({
                        "type": "crash",
                        "multiplier": crash_at
                    })
                    break

                await ws.send_json({
                    "type": "multiplier",
                    "multiplier": multiplier
                })

                await asyncio.sleep(0.1)

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        print("Player disconnected")
    except Exception as error:
        print("WebSocket error:", error)
