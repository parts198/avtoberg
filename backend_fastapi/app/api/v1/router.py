from fastapi import APIRouter

from app.api.v1.endpoints import auth, orders, stores, sync_jobs

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(stores.router)
api_router.include_router(orders.router)

api_router.include_router(sync_jobs.router)
