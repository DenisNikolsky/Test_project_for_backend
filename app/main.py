from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db, async_engine
from app.base import Base
from app import crud, schemas
from app.tasks import celery_app, compute_device_stats, compute_user_stats
from typing import Optional

app = FastAPI(title="Device Stats Service")

@app.on_event("startup")
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/devices/{device_id}/data", response_model=schemas.DataPointResponse)
async def add_data_point(device_id: str, payload: schemas.DataPointCreate, db: AsyncSession = Depends(get_async_db)):
    # auto-create device if not exists
    await crud.get_or_create_device(db, device_id)
    point = await crud.create_data_point(db, device_id, payload.x, payload.y, payload.z)
    return point

@app.post("/devices/{device_id}/stats", response_model=schemas.TaskResponse)
async def start_device_stats(device_id: str, from_ts: Optional[str] = None, to_ts: Optional[str] = None):
    task = compute_device_stats.delay(device_id, from_ts, to_ts)
    return {"task_id": task.id}

@app.post("/users/{user_id}/stats", response_model=schemas.TaskResponse)
async def start_user_stats(user_id: int, from_ts: Optional[str] = None, to_ts: Optional[str] = None):
    task = compute_user_stats.delay(user_id, from_ts, to_ts)
    return {"task_id": task.id}

@app.get("/tasks/{task_id}")
async def get_task_result(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.failed():
        raise HTTPException(status_code=500, detail=str(task.info))
    if task.ready():
        return task.result
    return {"status": "pending", "task_id": task_id}

# User management
@app.post("/users", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.create_user(db, user.name)

@app.get("/users", response_model=list[schemas.UserResponse])
async def list_users(db: AsyncSession = Depends(get_async_db)):
    return await crud.get_users(db)

@app.post("/users/{user_id}/devices")
async def assign_device(user_id: int, device: schemas.DeviceAssign, db: AsyncSession = Depends(get_async_db)):
    dev = await crud.assign_device_to_user(db, device.device_id, user_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device assigned"}

@app.put("/devices/{device_id}/assign")
async def assign_device_direct(device_id: str, assign: schemas.DeviceAssign, db: AsyncSession = Depends(get_async_db)):
    dev = await crud.assign_device_to_user(db, device_id, assign.user_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device assigned"}

@app.get("/users/{user_id}/devices", response_model=list[schemas.DeviceResponse])
async def get_user_devices(user_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.get_user_devices(db, user_id)