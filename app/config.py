"""
Application configuration module.

Centralizes all environment-specific settings so they can be
overridden via environment variables in production deployments.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database file lives at backend/tickets.db
DATABASE_URL = f"sqlite:///{BASE_DIR / 'tickets.db'}"

# ---------------------------------------------------------------------------
# API metadata (used by Swagger / OpenAPI docs)
# ---------------------------------------------------------------------------
APP_TITLE = "AI Customer Support Automation Platform"
APP_DESCRIPTION = (
    "REST API for managing support tickets escalated from the n8n "
    "automation workflow when AI confidence is below the threshold."
)
APP_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# CORS – allow local frontends and n8n during development
# ---------------------------------------------------------------------------
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5678",   # default n8n port
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5678",
]
