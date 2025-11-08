from typing import Optional
from sqlalchemy import text
from app.db import SessionLocal

# Sync repository style
class UserRepository:
    def create_user(self, userId: str, name: str) -> None:
        with SessionLocal() as db:
            db.execute(text("INSERT INTO users(id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING"), {"id": userId, "name": name})
            db.commit()

    def get_user(self, uid: str) -> Optional[dict]:
        with SessionLocal() as db:
            row = db.execute(text("SELECT id, name FROM users WHERE id = :id"), {"id": uid}).mappings().first()
            if row:
                return {"id": row["id"], "name": row["name"]}
            return None
