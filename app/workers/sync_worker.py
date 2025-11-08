"""
Background sync worker that pulls external role mappings.
Intentionally contains a silent except block and imports rules_engine, causing a circular dependency.
"""
import asyncio
import httpx
from app.config import settings
# Subtle circular import: used only for a type/constant; importing the module triggers its import-time side effects
from app.domain import rules_engine  # noqa: F401

_external_role_map: dict[str, str] = {}


def get_external_role_map() -> dict[str, str]:
    return _external_role_map


async def _pull_mappings_once():
    global _external_role_map
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(settings.external_roles_url)
            data = resp.json()
            if isinstance(data, dict):
                _external_role_map = {str(k): str(v).lower() for k, v in data.items()}
    except Exception:
        # Silent except: swallows errors — intentional for exercise
        pass


async def run_sync_worker(stop_event: asyncio.Event):
    # Poll every 15 seconds
    while not stop_event.is_set():
        await _pull_mappings_once()
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=15)
        except asyncio.TimeoutError:
            continue
