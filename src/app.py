from contextlib import asynccontextmanager
from uvicorn import run
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import routers
from database import (
    Base,
    async_engine
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title='Async FastAPI (User Auth API)',
    version='1.0.0',
    swagger_ui_parameters={'defaultModelsExpandDepth': -1},
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*']
)

for router in routers:
    app.include_router(router)

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
