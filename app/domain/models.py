from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    name: str

class Team(BaseModel):
    id: str
    name: str

class Membership(BaseModel):
    user_id: str
    team_id: str
    role: str

class PermissionCheck(BaseModel):
    user_id: str
    resource_id: str
    action: str
    context: Optional[dict] = None
