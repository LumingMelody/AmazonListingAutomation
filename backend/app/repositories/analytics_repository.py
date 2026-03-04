from datetime import date
from decimal import Decimal
from typing import Any

from app.db.models.analytics import ListingMetricsORM
from app.repositories.base import BaseRepository


class ListingMetricsRepository(BaseRepository):
    def create(self, **payload: Any) -> ListingMetricsORM:
        if isinstance(payload.get("date"), str):
            payload["date"] = date.fromisoformat(payload["date"])
        if isinstance(payload.get("ordered_product_sales"), str):
            payload["ordered_product_sales"] = Decimal(payload["ordered_product_sales"])

        model = ListingMetricsORM(**payload)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_by_asin(self, asin: str) -> list[ListingMetricsORM]:
        return self.db.query(ListingMetricsORM).filter(ListingMetricsORM.asin == asin).all()

