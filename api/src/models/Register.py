from datetime import datetime
from uuid import UUID
from sqlmodel import Field, SQLModel, table

class Register(SQLModel, table=True):
    registerid: UUID = Field(primary_key=True, nullable=False)
    clientip: str = Field(nullable=False)
    registerdatetime: datetime = Field(nullable=False)
    query: str = Field(nullable=False)
    success: bool = Field(nullable=False)
    useragent: str = Field(nullable=False)
    