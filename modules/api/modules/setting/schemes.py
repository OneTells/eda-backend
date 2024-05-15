from pydantic import BaseModel


class SettingData(BaseModel):
    id: int
    value: int
