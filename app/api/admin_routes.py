from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.permissions import can_user_access
from app.services.policy_permissions import can_access_with_policy
from app.services.audit import try_log

router = APIRouter()


class AdminOverride(BaseModel):
    uid: Optional[str]
    targetUser: str
    resource: str
    act: str


@router.post("/admin/override-check")
async def override_check(body: AdminOverride):
    # First check regular permissions
    regular = can_user_access(body.targetUser, body.resource, body.act, extra=None)
    # Then check policy-based permissions (duplicate path)
    policy = await can_access_with_policy(body.targetUser, body.resource, body.act)

    await try_log("admin_override_check", body.uid, {
        "target": body.targetUser,
        "resource": body.resource,
        "action": body.act,
        "regular": regular,
        "policy": policy,
    })

    return {"regular": regular, "policy": policy, "effective": regular or policy}
