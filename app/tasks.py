from celery import Celery
from app.config import REDIS_URL, SYNC_DATABASE_URL
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from app.models import DataPoint, Device
from statistics import median
from datetime import datetime
from typing import List, Dict, Any

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)

def _compute_stats(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {"min": None, "max": None, "count": 0, "sum": 0.0, "median": None}
    return {
        "min": min(values),
        "max": max(values),
        "count": len(values),
        "sum": sum(values),
        "median": median(values),
    }

@celery_app.task(bind=True)
def compute_device_stats(self, device_id: str, from_ts: str = None, to_ts: str = None):
    session = SyncSession()
    try:
        query = session.query(DataPoint).filter(DataPoint.device_id == device_id)
        if from_ts:
            dt_from = datetime.fromisoformat(from_ts.replace('Z', '+00:00'))
            query = query.filter(DataPoint.timestamp >= dt_from)
        if to_ts:
            dt_to = datetime.fromisoformat(to_ts.replace('Z', '+00:00'))
            query = query.filter(DataPoint.timestamp <= dt_to)

        points = query.all()
        x_vals = [p.x for p in points]
        y_vals = [p.y for p in points]
        z_vals = [p.z for p in points]

        result = {
            "x": _compute_stats(x_vals),
            "y": _compute_stats(y_vals),
            "z": _compute_stats(z_vals),
        }
        return result
    finally:
        session.close()

@celery_app.task(bind=True)
def compute_user_stats(self, user_id: int, from_ts: str = None, to_ts: str = None):
    session = SyncSession()
    try:
        devices = session.query(Device).filter(Device.user_id == user_id).all()
        device_ids = [d.device_id for d in devices]

        overall_x, overall_y, overall_z = [], [], []
        dev_stats = {}

        for dev_id in device_ids:
            query = session.query(DataPoint).filter(DataPoint.device_id == dev_id)
            if from_ts:
                dt_from = datetime.fromisoformat(from_ts.replace('Z', '+00:00'))
                query = query.filter(DataPoint.timestamp >= dt_from)
            if to_ts:
                dt_to = datetime.fromisoformat(to_ts.replace('Z', '+00:00'))
                query = query.filter(DataPoint.timestamp <= dt_to)

            points = query.all()
            xv = [p.x for p in points]
            yv = [p.y for p in points]
            zv = [p.z for p in points]
            dev_stats[dev_id] = {
                "x": _compute_stats(xv),
                "y": _compute_stats(yv),
                "z": _compute_stats(zv),
            }
            overall_x.extend(xv)
            overall_y.extend(yv)
            overall_z.extend(zv)

        total_stats = {
            "x": _compute_stats(overall_x),
            "y": _compute_stats(overall_y),
            "z": _compute_stats(overall_z),
        }
        return {"devices": dev_stats, "total": total_stats}
    finally:
        session.close()