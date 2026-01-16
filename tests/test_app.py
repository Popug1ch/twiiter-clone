"""Тестовое приложение без startup_event."""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

test_app = FastAPI(title="Microblog API (Test)", version="1.0.0")

test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/media", exist_ok=True)

@test_app.get("/health")
async def health():
    return {"status": "healthy"}

@test_app.get("/")
async def root():
    return {"message": "Test API"}

@test_app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon in tests"}
