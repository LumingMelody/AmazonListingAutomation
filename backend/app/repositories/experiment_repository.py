from datetime import datetime
from typing import Any

from app.db.models.experiment import ListingLifecycleORM
from app.repositories.base import BaseRepository


class ListingLifecycleRepository(BaseRepository):
    def upsert_by_asin(self, *, asin: str, **payload: Any) -> ListingLifecycleORM:
        existing = self.db.query(ListingLifecycleORM).filter(ListingLifecycleORM.asin == asin).first()
        if existing is None:
            record = ListingLifecycleORM(asin=asin, **payload)
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

        for key, value in payload.items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(existing)
        return existing

