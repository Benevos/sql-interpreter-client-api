from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from os.path import realpath
from utils.Parser import SQLParser
from models.Query import Query
from models.Register import Register
from services.db_config import SessionDep, create_db_and_tables
from starlette.requests import Request
from uuid import uuid4
import pandas as pd
import logging

TABLES_PATH = realpath(__file__).replace("\\", "/").replace("src/app.py", "data/").lower()

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def welcome_message():
    return {"message": "Hello, user"}

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

    tables_df = pd.read_csv(TABLES_PATH + "tables.csv")
    tables_df.loc[len(tables_df)] = [table_alias, file.filename]
    tables_df.to_csv(TABLES_PATH + "tables.csv", index=False)
    
    parser.tables.update({table_alias: file.filename})
    
    return {"filename": file.filename, "message": "Archivo subido y registrado exitosamente.", "alias": table_alias}

@app.post("/query")
def process_query(query: Query, request: Request, session: SessionDep):
    
    success, message, tokens = parser.parse(query.content)
    
    print(request.headers)
    
    regsiter = Register(
        registerid = uuid4(),
        clientip = request.client,
        registerdatetime = datetime.now(),
        query = query.content,
        success = success,
        useragent = request.headers["user-agent"]
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
       
    
    
    