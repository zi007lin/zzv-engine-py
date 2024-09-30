import time
import uuid
from typing import List

from pydantic import BaseModel


class Snapshot(BaseModel):
    class Config:
        extra = 'allow'  # Allow dynamic fields


class SnapshotList(BaseModel):
    snapshots: List[Snapshot]  # List of snapshot objects
    key: str  # UUID for the SnapshotList
    time: int  # Timestamp in milliseconds for the SnapshotList
    name: str  # Default name, set to "XLK"

    # Initialize default values for key, time, and name at the list level
    def __init__(self, **data):
        data['key'] = str(uuid.uuid4())  # Generate a UUID for the entire SnapshotList
        data['time'] = int(time.time() * 1000)  # Current time in milliseconds
        data['name'] = "XLK"  # Default name
        super().__init__(**data)
