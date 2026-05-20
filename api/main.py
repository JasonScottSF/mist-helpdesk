from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, sites, clients, marvis

app = FastAPI(title="Mist Helpdesk API", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/api/auth",    tags=["auth"])
app.include_router(sites.router,   prefix="/api/sites",   tags=["sites"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(marvis.router,  prefix="/api/marvis",  tags=["marvis"])


@app.get("/api/health")
async def health():
    return {"ok": True}
