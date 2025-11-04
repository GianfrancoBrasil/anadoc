from fastapi import FastAPI
from fastapi.routing import APIRoute
from typing import List

app = FastAPI()

@app.get("/")
def root():
    # prova de vida: responde em /api/fast_health
    return {"ok": True, "where": "/api/fast_health"}

@app.get("/routes")
def list_routes() -> List[str]:
    # lista todas as rotas que ESTE app enxerga
    return [getattr(r, "path", str(r)) for r in app.router.routes]

# catch-all para debug: se o roteamento do Vercel “mexer” no caminho,
# você verá aqui qual path realmente chegou ao app.
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def echo_path(path: str):
    return {"received_path": f"/{path}"}