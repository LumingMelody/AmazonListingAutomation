import re
from typing import Any, Dict, List


class ListingQAService:
    """Listing 上架质量检查服务。"""

    def __init__(self) -> None:
        self.required_fields = ["title", "bullet_points", "description", "main_image", "price"]

    def check_listing(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        scores: List[float] = []

        completeness_result = self._check_field_completeness(listing_data)
        issues.extend(completeness_result["issues"])
        scores.append(completeness_result["score"])

        title_result = None
        if "title" in listing_data:
            title_result = self.validate_title(str(listing_data["title"]))
            if not title_result["valid"]:
                issues.extend(title_result["issues"])
            scores.append(1.0 if title_result["valid"] else 0.5)

        bullet_result = None
        if "bullet_points" in listing_data:
            bullet_result = self._check_bullet_points(listing_data["bullet_points"])
            issues.extend(bullet_result["issues"])
            scores.append(bullet_result["score"])

        image_result = None
        if "main_image" in listing_data:
            image_result = self._check_image_spec(str(listing_data["main_image"]))
            issues.extend(image_result["issues"])
            scores.append(image_result["score"])

        total_score = (sum(scores) / len(scores)) if scores else 0.0

        if total_score >= 0.8:
            status = "pass"
        elif total_score >= 0.6:
            status = "warning"
        else:
            status = "fail"

        return {
            "score": total_score,
            "status": status,
            "issues": issues,
            "details": {
                "completeness": completeness_result,
                "title": title_result,
                "bullet_points": bullet_result,
                "image": image_result,
            },
        }

    def validate_title(self, title: str) -> Dict[str, Any]:
        issues: List[str] = []

        if len(title) < 20:
            issues.append("标题过短（建议至少20字符）")
        elif len(title) > 200:
            issues.append("标题过长（建议不超过200字符）")

        if title.isupper():
            issues.append("标题不应全部大写")

        if re.search(r"[!@#$%^&*()]", title):
            issues.append("标题包含不建议的特殊字符")

        return {"valid": len(issues) == 0, "issues": issues}

    def _check_field_completeness(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        missing_fields: List[str] = []

        for field in self.required_fields:
            if field not in listing_data or not listing_data[field]:
                missing_fields.append(field)
                issues.append(f"缺少必填字段: {field}")

        score = 1.0 - (len(missing_fields) / len(self.required_fields))
        return {"score": score, "issues": issues, "missing_fields": missing_fields}

    def _check_bullet_points(self, bullet_points: List[str]) -> Dict[str, Any]:
        issues: List[str] = []

        if len(bullet_points) < 3:
            issues.append("五点描述至少需要3条")
        elif len(bullet_points) > 5:
            issues.append("五点描述不应超过5条")

        for i, point in enumerate(bullet_points):
            if len(point) < 10:
                issues.append(f"第{i + 1}条描述过短")
            elif len(point) > 500:
                issues.append(f"第{i + 1}条描述过长")

        score = 1.0 if not issues else 0.7
        return {"score": score, "issues": issues}

    def _check_image_spec(self, image_path: str) -> Dict[str, Any]:
        issues: List[str] = []
        valid_extensions = [".jpg", ".jpeg", ".png"]

        if not any(image_path.lower().endswith(ext) for ext in valid_extensions):
            issues.append("图片格式不符合要求（支持JPG/PNG）")

        score = 1.0 if not issues else 0.5
        return {"score": score, "issues": issues}
