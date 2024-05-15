from datetime import datetime

from pydantic import BaseModel


class Record(BaseModel):
    id: int
    title: str
    photo: str
    created_at: datetime
