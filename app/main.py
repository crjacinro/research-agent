import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.api import agents
from app.core.db import init_db, close_db
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await close_db()

def create_app() -> FastAPI:
    fastapi_app = FastAPI(title="Research Agent API", version="1.0", lifespan=lifespan)
    fastapi_app.include_router(agents.router)
    return fastapi_app

app = create_app()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """
    Handles RequestValidationError and returns a 400 Bad Request response.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Bad Request: Invalid data provided.", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(_: Request):
    """
    Handles all unhandled exceptions in the application.
    """
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred while processing the request."},
    )