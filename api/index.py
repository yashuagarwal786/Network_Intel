"""Vercel ASGI entry point for the VEIL demo API."""
import os
from pathlib import Path


state_dir = Path("/tmp/veil-state")
state_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("VEIL_INTAKE_DB", str(state_dir / "intake.sqlite3"))
os.environ.setdefault("VEIL_REVIEW_DB", str(state_dir / "investigator_journal.sqlite3"))
os.environ.setdefault("VEIL_RESOLUTION_DB", str(state_dir / "resolution.sqlite3"))

from backend.main import app  # noqa: E402,F401
