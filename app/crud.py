from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Device, DataPoint
from datetime import datetime
from typing import Optional

async def create_user(db: AsyncSession, name: str) -> User:
    user = User(name=name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def get_or_create_device(db: AsyncSession, device_id: str) -> Device:
    result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        device = Device(device_id=device_id)
        db.add(device)
        await db.commit()
        await db.refresh(device)
    return device

async def assign_device_to_user(db: AsyncSession, device_id: str, user_id: int) -> Optional[Device]:
    result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if device:
        device.user_id = user_id
        await db.commit()
        await db.refresh(device)
    return device

async def create_data_point(db: AsyncSession, device_id: str, x: float, y: float, z: float, timestamp: Optional[datetime] = None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    point = DataPoint(device_id=device_id, x=x, y=y, z=z, timestamp=timestamp)
    db.add(point)
    await db.commit()
    await db.refresh(point)
    return point

async def get_user_devices(db: AsyncSession, user_id: int):
    result = await db.execute(select(Device).where(Device.user_id == user_id))
    return result.scalars().all()