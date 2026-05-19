from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional, List, Union

class DataPointCreate(BaseModel):
    x: float
    y: float
    z: float

class DataPointResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    x: float
    y: float
    z: float

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class DeviceAssign(BaseModel):
    user_id: int

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class StatsResult(BaseModel):
    min: float
    max: float
    count: int
    sum: float
    median: float

class DeviceStatsResponse(BaseModel):
    x: StatsResult
    y: StatsResult
    z: StatsResult

class UserStatsResponse(BaseModel):
    devices: Dict[str, DeviceStatsResponse]
    total: DeviceStatsResponse

class TaskResponse(BaseModel):
    task_id: str