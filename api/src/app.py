from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from os.path import realpath
from utils.Parser import SQLParser
from models.Query import Query
from models.Register import Register
from services.db_config import SessionDep, create_db_and_tables
from uuid import uuid4
import logging

TABLES_PATH = realpath(__file__).replace("\\", "/").replace("src/utils/Parser.py", "data/").lower()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('App Started')
    create_db_and_tables()
    yield
    logger.info('App Shutdown')
    
app = FastAPI(lifespan=lifespan)

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

parser = SQLParser()

@app.get("/")
def welcome_message():
    return {"message": "Hello, user"}

from fastapi import Form  # Import necesario para recibir datos como Form

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), table_alias: str = Form(...)):

    if not file.filename.endswith(".csv"):
        return JSONResponse(
            status_code=400,
            content={"message": "El archivo debe ser un archivo CSV."}
        )
    
    try:
        content = await file.read()
        content_decoded = content.decode("utf-8")
        rows = content_decoded.splitlines()
        if len(rows) < 2:
            return JSONResponse(
                status_code=400,
                content={"message": "El archivo CSV debe tener al menos una fila de datos además de las cabeceras."}
            )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Error al procesar el archivo CSV: {str(e)}"}
        )

    file_path = f"{TABLES_PATH}/{file.filename}"
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error al guardar el archivo: {str(e)}"}
        )
    
    if not table_alias:
        return JSONResponse(
            status_code=400,
            content={"message": "El alias de la tabla es obligatorio."}
        )
    
    parser.tables.update({table_alias: file_path})
    
    return {"filename": file.filename, "message": "Archivo subido y registrado exitosamente.", "alias": table_alias}

@app.post("/query")
def process_query(query: Query, session: SessionDep):
    
    success, message, tokens = parser.parse(query.content)
    
    regsiter = Register(
        registerid = uuid4(),
        registerdatetime = datetime.now(),
        query = query.content,
        success = success
    )
    
    session.add(regsiter)
    session.commit()
    session.refresh(regsiter)
    
    if not success:
        return JSONResponse(
            status_code = 400,
            content = {
                "success": success,
                "message": message,
                "tokens": tokens
            }
        )

    return JSONResponse(
        status_code = 200,
        content = {
            "success": success,
            "message": message,
            "tokens": tokens
        }
    )
       
    
    
    