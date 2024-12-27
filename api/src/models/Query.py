from pydantic import BaseModel

class Query(BaseModel):
    content: str