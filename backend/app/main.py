from fastapi import FastAPI
from sqlalchemy import text

from app.api.farms import router as farms_router
from app.database.database import Base, engine, get_db
from app.database import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartFarm Backend", version="1.0.0")
app.include_router(farms_router)


@app.get("/api/health", tags=["system"])
def health():
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}