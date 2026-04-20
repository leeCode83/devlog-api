from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.lib.errors import register_error_handlers, configure_logging
from app.modules.auth.router import router as auth_router


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

    app.openapi_components = {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    }

    register_error_handlers(app)

    app.include_router(auth_router, prefix="/api/v1")

    return app


app = create_app()