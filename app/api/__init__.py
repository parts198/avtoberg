from fastapi import APIRouter
from .routes import auth, stores, products, product_groups, warehouses, stocks, orders, promotions, logs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(product_groups.router, prefix="/product-groups", tags=["product-groups"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
