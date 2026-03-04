from typing import Any, Dict, List


class DataImportService:
    """数据导入服务。"""

    def import_ad_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入广告表现数据。"""
        imported = 0
        errors: List[Dict[str, Any]] = []

        for row in data:
            try:
                # TODO: replace with actual database persistence.
                _ = row
                imported += 1
            except Exception as exc:  # pragma: no cover
                errors.append({"row": row, "error": str(exc)})

        return self._build_result(imported, errors)

    def import_listing_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入 Listing 指标数据。"""
        imported = 0
        errors: List[Dict[str, Any]] = []

        for row in data:
            try:
                # TODO: replace with actual database persistence.
                _ = row
                imported += 1
            except Exception as exc:  # pragma: no cover
                errors.append({"row": row, "error": str(exc)})

        return self._build_result(imported, errors)

    @staticmethod
    def _build_result(imported: int, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "success": len(errors) == 0,
            "imported": imported,
            "errors": errors,
        }
