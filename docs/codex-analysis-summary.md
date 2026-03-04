# Codex 技术分析总结：Dify Workflow vs 当前项目

## Codex 的关键发现

### 1. 架构评估

**✅ 宏观架构正确：**
- API + 合规 + QA + 实验 + 适配器的分层设计是合理的
- 企业级模块（告警/分析/实验/监控）已经到位

**❌ 缺失的关键层：**
- **字段映射领域层**（Field Mapping Domain Layer）
- 当前 BU2Ama 适配器太薄，只传递 `mode/template_type/skus/product_info`
- 没有类型化的字段 schema、依赖关系或字段级验证

### 2. 当前实现的问题

**问题 1：适配器契约过于简单**
```python
# 当前：只有 4 个字段
ProcessRequestDTO(
    mode="add-color",
    template_type="DaMaUS",
    skus=["SKU1"],
    product_info={"title": "...", "description": "..."}
)
```
- 无法处理 264+ 个 EPUS 字段
- 没有字段类型定义
- 没有依赖关系验证

**问题 2：QA/合规检查粗糙**
```python
# excel.py:28 - 只检查 title + description
compliance_result = compliance_service.check_text(text_to_check)

# excel.py:61 - QA 结果是硬编码的
"qa_result": {"status": "pass", "score": 1.0} if result.success else {"status": "fail", "score": 0.0}
```

**问题 3：企业模块未集成到字段生成**
- 告警、分析、实验模块存在
- 但没有影响字段级别的 Listing 生成决策

## Codex 的建议

### Q1: 是否提取 Dify 的字段映射逻辑？

**✅ 是，但要提取为声明式规则，而非 264 节点的工作流**

提取内容：
- `FieldSchema`（类型、必填、允许值、依赖关系）
- `MappingRule`（源路径、转换、回退/默认值、条件）

### Q2: 如何集成 EPUS 字段到 BU2Ama 适配器？

**保持适配器薄，添加新的预适配器构建器：**

```
API 请求
  ↓
Schema 验证 (FieldValidator)
  ↓
规则映射 (RuleEngine + MappingRule)
  ↓
Payload 构建 (ListingPayloadBuilder)
  ↓
适配器调用 (BU2AmaAdapter)
```

新增组件：
- `ListingPayloadBuilder`（schema-aware）
- `FieldValidator`（必填/枚举/依赖检查）
- `RuleEngine`（应用 EPUS 映射）

### Q3: 当前架构是否足够？

**系统级别：✅ 足够**
**Listing 生成内部：❌ 不足够**

需要 Dify 级别的粒度，但**只在映射层**，不是把整个后端变成工作流节点。

### Q4: 如何干净地处理 264+ 字段？

**5 个最佳实践：**

1. **版本化 Schema 注册表**
   ```python
   # 数据文件，不是硬编码
   schemas = {
       "epus_v1": EPUSSchemaV1,
       "epus_v2": EPUSSchemaV2,
   }
   ```

2. **按领域分组字段**
   ```python
   field_groups = {
       "variation": [...],
       "compliance": [...],
       "offer": [...],
       "logistics": [...]
   }
   ```

3. **转换函数作为插件库**
   ```python
   # 小的、确定性的函数
   def map_color(erp_color: str) -> str:
       return COLOR_DICT.get(erp_color, erp_color)
   ```

4. **黄金测试 + 快照输出**
   ```python
   # 为主要类别添加测试
   test_epus_wedding_dress()
   test_epus_apparel_basic()
   ```

5. **兼容模式**
   ```python
   # 同时发送旧格式和新格式
   {
       "product_info": {...},  # 旧格式
       "mapped_fields": {...}  # 新格式
   }
   ```

## 实施建议

### 短期（立即可做）

**1. 创建字段映射服务层**
```
app/services/listing_schema/
├── __init__.py
├── field_schema.py      # FieldSchema 定义
├── mapping_rules.py     # MappingRule 定义
├── field_validator.py   # 字段验证器
├── rule_engine.py       # 规则引擎
└── schemas/
    ├── epus_v1.json     # EPUS schema 定义
    └── mappings/
        ├── color_map.json
        ├── size_map.json
        └── closure_map.json
```

**2. 扩展 DTO**
```python
class ProcessRequestDTO(BaseModel):
    mode: str
    template_type: str
    skus: List[str]
    product_info: Optional[Dict[str, Any]] = None

    # 新增字段
    marketplace: str = "US"  # US/EU/JP
    product_type: str = "apparel"
    attributes: Dict[str, Any] = {}
    schema_version: str = "v1"
```

**3. 在 API 中添加映射服务调用**
```python
# app/api/excel.py
from app.services.listing_schema.mapping_service import MappingService

mapping_service = MappingService()

@router.post("/api/process")
async def process_excel(request: ProcessRequest):
    # 1. 合规检查（现有）
    compliance_result = compliance_service.check_text(...)

    # 2. 字段映射（新增）
    mapped_fields = mapping_service.map_fields(
        template_type=request.template_type,
        product_info=request.product_info,
        schema_version="epus_v1"
    )

    # 3. 字段验证（新增）
    validation_result = mapping_service.validate_fields(mapped_fields)

    # 4. 调用适配器
    result = adapter.process_excel(...)
```

**4. 添加字段级 QA 输出**
```python
{
    "success": True,
    "output_file": "...",
    "qa_result": {
        "status": "pass",
        "score": 0.95,
        "field_issues": {
            "missing": ["care_instructions"],
            "invalid": ["price: must be > 0"],
            "warnings": ["bullet_point5: too short"]
        }
    }
}
```

### 中期（1-2 周）

**5. 从 Dify YAML 提取映射字典**
```bash
# 提取颜色映射
grep -A 50 "color_dict" AI上新助手-亚马逊EPUS\ V1.0.yml > color_map.json

# 提取尺码映射
grep -A 50 "size_dict" AI上新助手-亚马逊EPUS\ V1.0.yml > size_map.json

# 提取闭合类型映射
grep -A 50 "erp_map" AI上新助手-亚马逊EPUS\ V1.0.yml > closure_map.json
```

**6. 实现 Feature Flag**
```python
# app/config.py
ENABLE_FIELD_MAPPING = os.getenv("ENABLE_FIELD_MAPPING", "false").lower() == "true"
FIELD_MAPPING_TEMPLATES = os.getenv("FIELD_MAPPING_TEMPLATES", "EPUS").split(",")

# app/api/excel.py
if ENABLE_FIELD_MAPPING and request.template_type in FIELD_MAPPING_TEMPLATES:
    # 使用新的字段映射服务
    mapped_fields = mapping_service.map_fields(...)
else:
    # 使用旧的逻辑
    result = adapter.process_excel(request)
```

### 长期（1-2 月）

**7. 完整的 Schema 注册表**
- 支持多个站点（US/EU/JP）
- 支持多个产品类型（apparel/electronics/home）
- 版本化管理

**8. 可视化字段映射编辑器**
- Web UI 管理映射规则
- 实时预览映射结果
- 导入/导出映射配置

**9. 字段级监控和分析**
- 哪些字段经常缺失
- 哪些字段验证失败率高
- 字段质量趋势分析

## Codex 的提议

> "If you want, I can draft the concrete `FieldSchema`/`MappingRule` models and the first EPUS integration patch in this repo."

**建议接受 Codex 的提议，让它实现：**
1. `FieldSchema` 和 `MappingRule` 模型定义
2. 第一个 EPUS 集成补丁
3. 示例映射配置文件

## 总结

### 核心观点

1. **不要迁移 Dify 的 264 节点工作流**
   - 那是低代码平台的实现细节
   - 我们需要的是**映射逻辑**，不是**工作流引擎**

2. **添加字段映射领域层**
   - 这是当前架构缺失的关键部分
   - 不破坏现有架构，只是增强

3. **保持适配器薄**
   - 适配器只负责 HTTP 调用
   - 映射逻辑在适配器之前完成

4. **声明式配置优于命令式代码**
   - 字段 schema 和映射规则用 JSON/YAML 配置
   - 不要硬编码 264 个字段的处理逻辑

### 下一步行动

**立即执行：**
1. 让 Codex 实现 `FieldSchema`/`MappingRule` 模型
2. 创建 `app/services/listing_schema/` 目录结构
3. 从 Dify YAML 提取第一批映射字典（颜色、尺码、闭合类型）

**本周完成：**
1. 实现基础的字段映射服务
2. 在 `/api/process` 中集成映射服务
3. 添加 Feature Flag 控制

**下周完成：**
1. 完善字段验证逻辑
2. 添加字段级 QA 输出
3. 编写测试覆盖新功能
