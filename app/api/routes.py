from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.repositories.users import UserRepository
from app.repositories.teams import TeamRepository
from app.repositories.resources import ResourceRepository
from app.services.permissions import can_user_access

router = APIRouter()

user_repo = UserRepository()
team_repo = TeamRepository()
resource_repo = ResourceRepository()


class CreateUser(BaseModel):
    userId: str
    name: str


class CreateTeam(BaseModel):
    team_id: str
    team_name: str


class CreateMembership(BaseModel):
    uid: str
    team_id: str
    role: str


@router.post("/users")
async def create_user(body: CreateUser):
    user_repo.create_user(body.userId, body.name)
    return {"id": body.userId}


@router.post("/teams")
async def create_team(body: CreateTeam):
    await team_repo.create_team(body.team_id, body.team_name)
    return {"id": body.team_id}


@router.post("/memberships")
async def create_membership(body: CreateMembership):
    await team_repo.add_membership(body.uid, body.team_id, body.role)
    return {"ok": True}


@router.get("/permissions/check")
async def check_permission(user_id: Optional[str], resource_id: str, action: str, public: bool | None = None):
    if not resource_id or not action:
        raise HTTPException(status_code=400, detail="resource_id and action required")
    # Intentional missing null check on user_id to demonstrate failure path in rules_engine
    allowed = can_user_access(user_id, resource_id, action, extra={"public": public is True})
    return {"allowed": allowed}
