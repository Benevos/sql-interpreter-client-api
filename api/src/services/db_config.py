from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel
import os

load_dotenv()

def get_session():
    with Session(engine) as session:
        yield session
        
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

DATABASE_URI = os.getenv("DATABASE_URI")

if not DATABASE_URI:
    raise Exception("Error: No databse URI")

engine = create_engine(url=DATABASE_URI)
SessionDep = Annotated[Session, Depends(get_session)]