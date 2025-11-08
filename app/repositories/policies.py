from typing import Optional
import asyncpg
from app.config import settings

# Async repo for resource policies
class PolicyRepository:
    async def upsert_policy(self, resource_id: str, action: str, required_role: str) -> None:
        conn = await asyncpg.connect(dsn=settings.async_database_url.replace("+asyncpg", ""))
        try:
            await conn.execute(
                """
                INSERT INTO resource_policies(resource_id, action, required_role)
                VALUES($1, $2, $3)
                ON CONFLICT (resource_id, action)
                DO UPDATE SET required_role = EXCLUDED.required_role
                """,
                resource_id, action, required_role
            )
        finally:
            await conn.close()

    async def get_required_role(self, resource_id: str, action: str) -> Optional[str]:
        conn = await asyncpg.connect(dsn=settings.async_database_url.replace("+asyncpg", ""))
        try:
            row = await conn.fetchrow(
                "SELECT required_role FROM resource_policies WHERE resource_id=$1 AND action=$2",
                resource_id, action
            )
            return row["required_role"] if row else None
        finally:
            await conn.close()
