import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware('http')
async def request_logging(request: Request, call_next):
    try:
        response = await call_next(request)
        logger.info('%s %s -> %s', request.method, request.url.path, response.status_code)
        return response
    except Exception as exc:  # noqa: BLE001
        logger.exception('Unhandled API error: %s', exc)
        return JSONResponse(status_code=500, content={'detail': 'Internal server error'})


@app.get('/health')
def healthcheck():
    return {'status': 'ok'}
