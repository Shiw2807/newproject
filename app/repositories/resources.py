from sqlalchemy import text
from app.db import SessionLocal

# Another sync repository
class ResourceRepository:
    def create_resource(self, resource_id: str, type: str) -> None:
        with SessionLocal() as db:
            db.execute(text("INSERT INTO resources(id, type) VALUES (:id, :type) ON CONFLICT (id) DO NOTHING"), {"id": resource_id, "type": type})
            db.commit()
