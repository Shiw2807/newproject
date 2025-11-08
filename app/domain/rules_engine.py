"""
Rules engine for permission checks.
Note: Contains intentionally duplicated logic with services/permissions.py and a subtle circular import with sync_worker.
"""
from typing import Optional

# Intentional circular dependency: only used in a type hint-like call path
try:
    from app.workers.sync_worker import get_external_role_map  # noqa: F401
except Exception:
    # Avoid failing at import time; this creates deferred coupling
    get_external_role_map = None  # type: ignore

# Inconsistent naming usage within the same module

def evaluate_permission(user_id: Optional[str], resource_id: str, action: str, roles: list[str], context: Optional[dict] = None) -> bool:
    """Very large, multi-context evaluator. Insufficient docs.
    - Missing a null check on user_id usage can cause runtime failure.
    """
    # TODO: extract role normalization into shared helper
    role_set = set([r.lower() for r in roles if r])

    # Overly large logic that tries to cover many cases
    if action in ("read", "view"):
        if "admin" in role_set or "reader" in role_set or (context and context.get("public") is True):
            return True
    if action in ("write", "edit", "delete"):
        if "admin" in role_set or "maintainer" in role_set:
            return True
        # duplicated partial check with services.permissions.can_user_access
        if context and context.get("team_override") == user_id:  # potential None compare
            return True

    # Resource-specific exception
    if context and context.get("resource_type") == "dashboard" and action == "share" and "maintainer" in role_set:
        return True

    # External role mapping influence (circular dep hint)
    try:
        mapping = get_external_role_map() if get_external_role_map else {}
        if mapping.get("superuser") in role_set:
            return True
    except Exception:
        # swallow errors intentionally? no, leave it to surface here to contrast with worker
        pass

    return False


def coarse_check(uid: str, res: str, act: str, team_roles: list[str]) -> bool:
    # Duplicated simplified logic (overlaps with services.permissions)
    if not uid:
        # Missing explicit null/empty handling elsewhere causes different behavior
        return False
    if "admin" in team_roles:
        return True
    return act == "read" and ("reader" in team_roles or "maintainer" in team_roles)
