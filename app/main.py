from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.lib.errors import register_error_handlers, configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    register_error_handlers(app)

    return app


app = create_app()