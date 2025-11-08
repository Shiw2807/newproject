"""
Service layer with duplicate logic vs domain.rules_engine.
Intentionally mixes async and sync calls by going to both repos.
"""
from typing import Optional
from app.repositories.users import UserRepository
from app.repositories.teams import TeamRepository
from app.domain.rules_engine import evaluate_permission  # duplicate path risk

user_repo = UserRepository()
team_repo = TeamRepository()


def can_user_access(uid: str, resource_id: str, action: str, *, extra: Optional[dict] = None) -> bool:
    # Partially duplicated decision logic with domain.rules_engine.evaluate_permission and coarse_check
    user = user_repo.get_user(uid)
    if user is None:
        # Missing null check in callers may cause runtime failure if uid is None
        return False

    # Gather roles (async call in sync function — anti-pattern for demo)
    import asyncio

    async def fetch_roles():
        return await team_repo.get_user_roles(uid)

    try:
        roles = asyncio.get_event_loop().run_until_complete(fetch_roles())
    except RuntimeError:
        # If already in an event loop (e.g., FastAPI), create a new loop — hacky
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        roles = new_loop.run_until_complete(fetch_roles())
        new_loop.close()
        asyncio.set_event_loop(None)

    role_names = [r["role"] for r in roles]

    # Duplicated logic piece
    if action in ("write", "delete") and ("admin" in role_names or "maintainer" in role_names):
        return True

    # Delegate to rules engine for broader rules
    return evaluate_permission(uid, resource_id, action, role_names, extra)
