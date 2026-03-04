# 实施计划：替代 Dify Workflow，实现相同输出

## 目标
使当前系统能够生成与 Dify workflow 完全相同的亚马逊 EPUS Listing Excel 文件。

## 挑战分析

### 1. 数据源差异
- **Dify**: 从 ERP 系统获取数据（未知格式）
- **当前系统**: 从 API 请求获取数据
- **解决方案**: 需要理解 Dify 的 ERP 数据格式，创建兼容的输入接口

### 2. 映射规则提取
- **Dify**: 264 个节点，每个节点有 Python 代码
- **当前系统**: 需要提取所有映射逻辑
- **解决方案**: 系统化提取 Dify YAML 中的所有代码块

### 3. 字段顺序和格式
- **Dify**: 精确控制 Excel 列顺序和格式
- **当前系统**: 需要完全匹配
- **解决方案**: 提取 Dify 的列顺序定义，实现相同的 Excel 生成逻辑

## 三阶段实施计划

### 阶段 1：基础架构 + 映射提取（第 1-2 周）

#### Week 1: 架构实现

**任务 1.1: 让 Codex 实现基础架构**
```bash
# Codex 实现
- FieldSchema 模型
- MappingRule 模型
- 字段映射服务框架
- 字段验证器
- 规则引擎
```

**任务 1.2: 提取 Dify 映射字典**
```bash
# 从 Dify YAML 提取所有映射字典
1. 颜色映射 (color_dict)
2. 尺码映射 (size_dict)
3. ERP 映射 (erp_map)
4. 产品类型映射 (c_dict)
5. 其他所有字典
```

**任务 1.3: 提取 Dify 代码逻辑**
```bash
# 提取所有 code 节点的 Python 代码
- 264 个节点的代码块
- 分类整理（生成逻辑 vs 插入逻辑）
- 识别依赖关系
```

#### Week 2: 字段 Schema 定义

**任务 2.1: 定义 EPUS 字段 Schema**
```json
{
  "schema_version": "epus_v1",
  "fields": [
    {
      "name": "product_type",
      "type": "string",
      "required": true,
      "position": 1,
      "mapping_rule": "product_type_mapping"
    },
    {
      "name": "seller_sku",
      "type": "string",
      "required": true,
      "position": 2,
      "mapping_rule": "seller_sku_generation"
    },
    // ... 264 个字段
  ]
}
```

**任务 2.2: 转换 Dify 代码为映射规则**
```python
# 示例：从 Dify 代码
def main(sku: str) -> dict:
    sku_list = [line.strip() for line in sku.split('\n')]
    return {"result": sku_list}

# 转换为映射规则
{
  "rule_name": "sku_processing",
  "input": "sku",
  "transform": "split_lines",
  "output": "sku_list"
}
```

**交付物：**
- ✅ 基础架构代码
- ✅ 所有映射字典（JSON 格式）
- ✅ EPUS 字段 Schema 定义
- ✅ 初步的映射规则库

### 阶段 2：逐字段对齐（第 3-6 周）

#### Week 3-4: 核心字段实现

**优先级 1：基础信息字段（20 个）**
```
1. product_type
2. seller_sku
3. brand_name
4. update
5. product_name
6. product_description
7. item_type
8. closure_type
9. care_instructions
10. price
11. quantity
12. gender
13. age
14. part_number
15. manufacturer
16. main_image_url
17. parent_child
18. parent_sku
19. relationship_type
20. variation_theme
```

**实施步骤：**
1. 为每个字段实现映射规则
2. 编写单元测试
3. 对比 Dify 输出验证
4. 调整直到完全一致

#### Week 5-6: 变体和样式字段（50 个）

**优先级 2：变体相关字段**
```
- apparel_size_system
- apparel_size_class
- apparel_size
- apparel_size_to
- apparel_body_type
- apparel_height_type
- size_name
- pattern_name
- pattern_type
- neck_style
- back_style
- waist_style
- item_length_description
- ... (共 50 个)
```

**实施步骤：**
1. 实现变体字段映射
2. 处理字段依赖关系
3. 验证变体组合逻辑
4. 对比测试

**交付物：**
- ✅ 70 个核心字段完全对齐
- ✅ 单元测试覆盖
- ✅ 对比测试报告

### 阶段 3：完整对齐 + 验证（第 7-8 周）

#### Week 7: 剩余字段实现

**优先级 3：其他字段（194 个）**
```
- 图片字段（other_image_url1-5, swatch_image_url）
- 营销字段（bullet_point1-5, generic_keywords）
- 定价字段（business_price, quantity_price1-3）
- 空列填充（多个占位列）
- 其他属性字段
```

**实施步骤：**
1. 批量实现剩余字段
2. 处理空列和占位符
3. 实现条件逻辑
4. 完整性测试

#### Week 8: 端到端验证

**任务 8.1: 创建对比测试套件**
```python
def test_dify_output_alignment():
    """对比 Dify 和当前系统的输出"""
    # 1. 准备相同的输入数据
    input_data = load_test_input()

    # 2. 运行 Dify workflow（手动或 API）
    dify_output = run_dify_workflow(input_data)

    # 3. 运行当前系统
    current_output = run_current_system(input_data)

    # 4. 逐字段对比
    diff = compare_outputs(dify_output, current_output)

    # 5. 断言一致性 >= 95%
    assert diff.consistency_rate >= 0.95
```

**任务 8.2: 黄金测试用例**
```bash
# 创建 10-20 个代表性测试用例
1. Wedding Dress (婚纱)
2. Men's T-Shirt (男士 T 恤)
3. Women's Jeans (女士牛仔裤)
4. Kids' Shoes (儿童鞋)
5. Accessories (配饰)
... (覆盖主要产品类型)
```

**任务 8.3: 差异分析和修复**
```bash
# 对于每个不一致的字段
1. 记录差异
2. 分析根本原因
3. 调整映射规则
4. 重新测试
5. 重复直到一致
```

**交付物：**
- ✅ 264 个字段全部实现
- ✅ 端到端测试套件
- ✅ 95%+ 输出一致性
- ✅ 差异分析报告

## 实施策略

### 并行工作流

```
Week 1-2: 基础架构
    ↓
Week 3-4: 核心字段 (Claude + Codex 并行)
    ↓
Week 5-6: 变体字段 (Claude + Codex 并行)
    ↓
Week 7: 剩余字段 (批量处理)
    ↓
Week 8: 验证和修复
```

### 质量保证

**每周检查点：**
- 周一：计划本周任务
- 周三：中期进度检查
- 周五：周总结 + 对比测试

**验收标准：**
- 每个字段有单元测试
- 每个字段通过对比测试
- 整体一致性 >= 95%
- 性能：生成时间 < 10 秒

## 风险和缓解

### 风险 1：Dify ERP 数据格式未知
**缓解：**
- 从 Dify YAML 反推数据格式
- 创建兼容的输入接口
- 如果无法获取真实 ERP 数据，使用模拟数据

### 风险 2：映射逻辑过于复杂
**缓解：**
- 分阶段实现，先易后难
- 使用 Codex 加速代码转换
- 保留 Dify 作为参考实现

### 风险 3：BU2Ama 引擎限制
**缓解：**
- 如果 BU2Ama 不支持某些字段，绕过它
- 直接生成 Excel（使用 openpyxl）
- 保持适配器模式，可以切换实现

### 风险 4：时间超出预期
**缓解：**
- 优先实现核心字段（80/20 原则）
- 使用并行工作流加速
- 如果需要，延长到 10-12 周

## 资源需求

### 人力
- Claude: 架构设计、复杂逻辑、测试验证
- Codex: 批量代码生成、映射规则转换
- 你: 需求确认、测试数据提供、验收

### 工具
- Python 3.11+
- openpyxl (Excel 生成)
- pytest (测试)
- pandas (数据处理)
- deepdiff (输出对比)

### 时间
- 最快：6 周（激进）
- 现实：8 周（推荐）
- 保守：10-12 周（包含缓冲）

## 下一步行动

### 立即开始（今天）

**1. 让 Codex 实现基础架构**
```bash
# 任务描述
"Implement FieldSchema and MappingRule models with field mapping service framework.

Requirements:
1. Create app/services/listing_schema/ directory structure
2. Implement FieldSchema model (field definition with type, required, position, etc.)
3. Implement MappingRule model (transform rules with input/output/condition)
4. Implement FieldValidator (validate fields against schema)
5. Implement RuleEngine (apply mapping rules)
6. Implement MappingService (orchestrate validation and mapping)
7. Add unit tests for all components

Reference: docs/codex-analysis-summary.md for architecture details."
```

**2. 提取 Dify 映射字典**
```bash
# 我来做这个
python3 extract_dify_mappings.py AI上新助手-亚马逊EPUS\ V1.0.yml
```

**3. 创建项目跟踪**
```bash
# 创建 GitHub Project 或 Notion Board
- 264 个字段的清单
- 每个字段的状态（待实现/进行中/已完成/已验证）
- 一致性测试结果
```

## 预期成果

**8 周后：**
- ✅ 完整的字段映射服务层
- ✅ 264 个 EPUS 字段全部实现
- ✅ 95%+ 输出一致性
- ✅ 完整的测试覆盖
- ✅ 可以完全替代 Dify workflow

**附加价值：**
- 更好的架构和可维护性
- 字段级质量控制
- 可扩展到其他站点（US/JP）
- 集成到企业级平台（合规、监控、分层）

---

**准备好开始了吗？** 我建议：
1. 先让 Codex 实现基础架构（今天）
2. 我提取 Dify 映射字典（今天）
3. 明天开始第一批核心字段的实现
