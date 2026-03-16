from pydantic import BaseModel, Field


class PriceLogEntryOut(BaseModel):
    id: int
    message: str
    created_at: str


class PriceRowOut(BaseModel):
    product_id: int
    offer_id: str
    title: str
    stock: int = 0
    fbs: int = 0
    fbo: int = 0
    current_price: float
    previous_price: float | None = None
    acquiring: float
    customer_delivery: float
    logistics: float
    first_mile: float
    packaging: float
    promotion: float
    ozon_commission_percent: float
    ozon_commission_rub: float
    cost_price: float
    fbs_cost: float
    payout_to_seller: float
    markup_percent: float
    margin_rub: float
    margin_percent: float


class PriceListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PriceRowOut]
    logs: list[PriceLogEntryOut] = []


class PriceOfferUpdateIn(BaseModel):
    offer_id: str
    new_price: float = Field(gt=0)


class PricePatchIn(BaseModel):
    new_price: float = Field(gt=0)


class PricesBulkUpdateIn(BaseModel):
    updates: list[PriceOfferUpdateIn]


class PricesApplyMarkupIn(BaseModel):
    markup_percent: float
    min_price_markup_percent: float = 0
    offer_ids: list[str] | None = None


class PricesReloadIn(BaseModel):
    store_id: int


class PricesReloadOut(BaseModel):
    status: str
    message: str

