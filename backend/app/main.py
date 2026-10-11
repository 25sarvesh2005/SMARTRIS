"""FastAPI application entry point for SmartRIS."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import API_VERSION
from .routes import router

app = FastAPI(title="SmartRIS API", version=API_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(router)

