from datetime import datetime

from pydantic import BaseModel


class OrderOut(BaseModel):
    id: int
    store_id: int
    external_order_id: str
    status: str
    order_date: datetime
    payload: dict

    class Config:
        from_attributes = True


class OrderDashboardItemOut(BaseModel):
    product_id: int | None = None
    offer_id: str = ''
    product_name: str = ''
    qty: int = 0
    price: float = 0
    revenue: float = 0
    expenses_allocated: float = 0
    markup_ratio_fact: float | None = None


class OrderDashboardRowOut(BaseModel):
    id: int
    posting_number: str
    status: str
    schema: str
    created_at: datetime
    store_id: int
    store_name: str
    first_offer_id: str = ''
    items_count: int = 0
    qty_total: int = 0
    revenue_total: float = 0
    expenses_total: float = 0
    markup_ratio_avg: float | None = None
    items: list[OrderDashboardItemOut]


class OrderDashboardSummaryOut(BaseModel):
    total_orders: int
    total_items: int
    total_units: int
    total_revenue: float
    total_expenses: float
    status_breakdown: list[dict]
    scope: str
    scope_label: str


class OrderDashboardStoreOut(BaseModel):
    id: int
    name: str


class OrderDashboardOut(BaseModel):
    stores: list[OrderDashboardStoreOut]
    filters: dict
    summary: OrderDashboardSummaryOut
    hourly: list[int]
    orders: list[OrderDashboardRowOut]
