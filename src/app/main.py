from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from app.config import Settings
from app.infrastructure.postgres.db import SqlAlchemyDatabaseManager
from app.ioc import create_container

from app.api.exceptions import setup_exception_handlers
from app.api.routes import router
from app.infrastructure.postgres.add_event_data import add_event_data_to_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.dishka_container
    db_manager = await container.get(SqlAlchemyDatabaseManager)

    try:
        await add_event_data_to_db(db_manager)
        yield
    finally:
        await container.close()


app = FastAPI(title="API Афиши", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
setup_exception_handlers(app)

setup_dishka(create_container(Settings()), app)
