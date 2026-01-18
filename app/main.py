import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, tweets, medias
from app.core.database import engine, Base

app = FastAPI(
    title="Microblog API",
    description="Корпоративный сервис микроблогов",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

@app.on_event("startup")
async def startup_event():
    os.makedirs("static/media", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# статика фронта
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIST, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIST, "js")), name="js")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(FRONTEND_DIST, "favicon.ico"))

# API ДО catch-all
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(tweets.router, prefix="/api", tags=["tweets"])
app.include_router(medias.router, prefix="/api", tags=["medias"])

@app.get("/health")
async def health():
    return {"status": "healthy"}

# главная страница SPA
@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

@app.get("/{path:path}", response_class=FileResponse)
async def spa_catchall(path: str, request: Request):
    if path.startswith("api/") or path == "health":
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
