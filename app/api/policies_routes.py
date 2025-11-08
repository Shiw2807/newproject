from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories.policies import PolicyRepository
from app.services.audit import try_log

router = APIRouter()
repo = PolicyRepository()


class UpsertPolicy(BaseModel):
    resourceId: str  # inconsistent naming
    action: str
    required_role: str


@router.post("/policies")
async def upsert_policy(body: UpsertPolicy):
    await repo.upsert_policy(body.resourceId, body.action, body.required_role)
    await try_log("policy_upsert", None, {"resource": body.resourceId, "action": body.action})
    return {"ok": True}
