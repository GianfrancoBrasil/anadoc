from fastapi import FastAPI
from fastapi.routing import APIRoute

app = FastAPI()

@app.get("/")
def health():
    return {"ok": True, "where": "/api/fast_health"}

@app.get("/routes")
def list_routes():
    return [r.path for r in app.routes]
