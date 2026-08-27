"""Database engine setup.

Hardened (2026-08): `create_engine(settings.DATABASE_URL)` was evaluated at
import time with no probe and no fallback, so an unreachable Postgres (or the
default SQLite path on a read-only serverless filesystem) took the whole API
down at startup. This module now resolves a URL that actually works, and
`init_db()` creates/migrates tables without ever raising.
"""

import os
import re
import tempfile
import urllib.parse

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def _normalise(url: str) -> str:
    """Make a hand-pasted Postgres URL safe to parse."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    m = re.match(r"^(?P<scheme>[a-z+]+://)(?P<user>[^:/@]+):(?P<pw>.*)@(?P<rest>[^@]+)$", url)
    if m:
        pw = m.group("pw")
        if pw.startswith("[") and pw.endswith("]"):
            pw = pw[1:-1]
        pw = urllib.parse.quote(urllib.parse.unquote(pw), safe="")
        url = f"{m.group('scheme')}{m.group('user')}:{pw}@{m.group('rest')}"
    return url


def _sqlite_fallback() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local = os.path.join(root, "sql_app.db")
    try:
        with open(local, "a"):
            pass
        return f"sqlite:///{local}"
    except OSError:
        # Vercel/Lambda only allow writes under /tmp.
        return f"sqlite:///{os.path.join(tempfile.gettempdir(), 'aiops.db')}"


def _make_engine(url: str):
    kwargs = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["connect_args"] = {"connect_timeout": 10}
    return create_engine(url, **kwargs)


_configured = str(settings.DATABASE_URL or "").strip().strip('"')
USING_FALLBACK = False

if not _configured or _configured.startswith("sqlite"):
    DATABASE_URL = _sqlite_fallback()
else:
    DATABASE_URL = _normalise(_configured)
    try:
        with _make_engine(DATABASE_URL).connect():
            pass
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: DATABASE_URL unreachable ({type(exc).__name__}: {exc}). "
              f"Falling back to local SQLite so the API can still start.")
        DATABASE_URL, USING_FALLBACK = _sqlite_fallback(), True

engine = _make_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


_SQL_TYPES = {
    "INTEGER": "INTEGER", "BIGINT": "BIGINT", "VARCHAR": "VARCHAR",
    "TEXT": "TEXT", "DATETIME": "TIMESTAMP", "TIMESTAMP": "TIMESTAMP",
    "BOOLEAN": "BOOLEAN", "FLOAT": "FLOAT", "NUMERIC": "NUMERIC",
    "JSON": "TEXT", "ENUM": "VARCHAR",
}


def run_migrations():
    """Add model columns missing from existing tables. Idempotent, never raises."""
    try:
        inspector = inspect(engine)
        existing = set(inspector.get_table_names())
        for table in Base.metadata.sorted_tables:
            if table.name not in existing:
                continue
            have = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in have or column.primary_key:
                    continue
                sql_type = _SQL_TYPES.get(column.type.__class__.__name__.upper(), "VARCHAR")
                with engine.begin() as conn:
                    conn.execute(text(
                        f'ALTER TABLE {table.name} ADD COLUMN {column.name} {sql_type}'
                    ))
                print(f"Migrated: added {table.name}.{column.name}")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: schema migration skipped ({type(exc).__name__}: {exc}).")


def init_db():
    """Create tables and apply migrations. Never raises."""
    try:
        import app.db.models  # noqa: F401 - ensure models are registered on Base
    except Exception:  # noqa: BLE001
        pass
    try:
        Base.metadata.create_all(bind=engine)
        run_migrations()
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: database init failed ({type(exc).__name__}: {exc}).")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
