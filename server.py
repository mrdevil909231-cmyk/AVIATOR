
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio
import random
import json
import time

app = FastAPI(title="AVIATOR")

BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return (BASE / "templates" / "index.html").read_text(encoding="utf-8")

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
            start = time.monotonic()

            await ws.send_json({"type": "waiting", "seconds": 5})
            await asyncio.sleep(5)

            await ws.send_json({"type": "started"})

            while True:
                elapsed = time.monotonic() - start - 5
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

    except Exception:
        pass
