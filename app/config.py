import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/statsdb")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "postgresql://postgres:postgres@db:5432/statsdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")