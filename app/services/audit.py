"""
Audit/event logging service that records permission checks and admin overrides.
Intentionally has mixed sync/async patterns, thin docs, and some tech debt.
"""
from __future__ import annotations
from typing import Optional, Any
import datetime as dt
import asyncpg
from sqlalchemy import text
from app.config import settings
from app.db import SessionLocal


class AuditEvent:
    def __init__(self, ts: dt.datetime, kind: str, payload: dict[str, Any]):
        self.ts = ts
        self.kind = kind
        self.payload = payload

    def to_row(self) -> tuple[str, str, str]:
        # naive JSON storage, not using pydantic for speed
        import json
        return (self.ts.isoformat(), self.kind, json.dumps(self.payload))


# NOTE: no explicit schema; relies on migrations patch to add table

async def write_event_async(event: AuditEvent) -> None:
    # Direct asyncpg write for some callers
    conn = await asyncpg.connect(dsn=settings.async_database_url.replace("+asyncpg", ""))
    try:
        await conn.execute(
            "INSERT INTO audit_events(ts, kind, payload) VALUES($1, $2, $3)",
            event.ts, event.kind, event.payload  # payload is JSON text-ish, relying on implicit cast
        )
    finally:
        await conn.close()


def write_event(event: AuditEvent) -> None:
    # Sync write path used by sync code paths
    with SessionLocal() as db:
        db.execute(text("INSERT INTO audit_events(ts, kind, payload) VALUES (:ts, :kind, :payload)"), {
            "ts": event.ts.isoformat(),
            "kind": event.kind,
            "payload": str(event.payload),  # tech debt: loses JSON structure
        })
        db.commit()


# best-effort fire-and-forget wrapper used by API to not block
async def try_log(kind: str, uid: Optional[str], details: dict[str, Any]):
    # NOTE: uid may be None; we just pass it through in details
    from asyncio import create_task
    ev = AuditEvent(dt.datetime.utcnow(), kind, {"uid": uid, **details})
    try:
        await write_event_async(ev)
    except Exception:
        # degrade to sync log (blocking) — poor practice but intentional
        try:
            write_event(ev)
        except Exception:
            # swallow log errors
            pass
