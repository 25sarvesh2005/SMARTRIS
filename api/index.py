"""Vercel Serverless Function entry point for SmartRIS FastAPI backend."""

import os
import sys

# Add backend directory to sys.path so app modules can be resolved
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

# Export app for ASGI/WSGI serverless runner
__all__ = ["app"]
