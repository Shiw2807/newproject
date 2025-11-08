from typing import Optional
import asyncpg
from app.config import settings

# Async repository style using asyncpg directly
class TeamRepository:
    async def create_team(self, team_id: str, team_name: str) -> None:
        conn = await asyncpg.connect(dsn=settings.async_database_url.replace("+asyncpg", ""))
        try:
            await conn.execute("""
                INSERT INTO teams(id, name) VALUES($1, $2)
                ON CONFLICT (id) DO NOTHING
            """, team_id, team_name)
        finally:
            await conn.close()

    async def add_membership(self, uid: str, team_id: str, role: str) -> None:
        conn = await asyncpg.connect(dsn=settings.async_database_url.replace("+asyncpg", ""))
        try:
            await conn.execute("""
                INSERT INTO memberships(user_id, team_id, role) VALUES($1, $2, $3)
                ON CONFLICT (user_id, team_id) DO UPDATE SET role = EXCLUDED.role
            """, uid, team_id, role)
        finally:
            await conn.close()

    async def get_user_roles(self, user_id: str) -> list[dict]:
        conn = await asyncpg.connect(dsn=settings.async_database_url.replace("+asyncpg", ""))
        try:
            rows = await conn.fetch("""
                SELECT m.team_id, m.role FROM memberships m WHERE m.user_id = $1
            """, user_id)
            return [{"team_id": r["team_id"], "role": r["role"]} for r in rows]
        finally:
            await conn.close()
