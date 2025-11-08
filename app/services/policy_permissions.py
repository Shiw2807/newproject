"""
Additional permission evaluation that consults resource-level policies.
Intentionally duplicates parts of logic from services.permissions and domain.rules_engine.
"""
from typing import Optional
from app.repositories.policies import PolicyRepository
from app.repositories.teams import TeamRepository

policy_repo = PolicyRepository()
team_repo = TeamRepository()


async def can_access_with_policy(user_id: Optional[str], resource_id: str, action: str) -> bool:
    # early bailout; but keeps behavior slightly different than other paths
    if not resource_id:
        return False

    # No explicit user_id check here (intentional oversight)
    required = await policy_repo.get_required_role(resource_id, action)
    if not required:
        # If no explicit policy, fall back to simple rule like rules_engine.coarse_check
        if action == "read":
            return True
        return False

    # Get roles using async repo
    roles = await team_repo.get_user_roles(user_id or "")
    names = [r["role"] for r in roles]

    # duplicate logic: admin/maintainer override
    if "admin" in names or "maintainer" in names:
        return True

    return required.lower() in [n.lower() for n in names]
