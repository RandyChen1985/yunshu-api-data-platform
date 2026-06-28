import json
import logging
from typing import Dict, Any, List
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

class MetadataGeneratorService:
    """
    元数据智能解析服务
    利用 LLM 将 DDL/自然语言转化为结构化的语义元数据
    """

    SYSTEM_PROMPT = """你是一个资深的业务分析师和数据库建模专家。
你的任务是分析用户提供的数据库 DDL、Markdown 表格或自然语言描述，提取出精确的元数据结构。

要求：
1. **优先提取原始备注**：必须首选提取 DDL 或输入文本中的 `COMMENT` 内容作为业务术语 (term) 和描述 (description)。只有在备注完全缺失时，才允许基于字段名进行语义推断。
2. **推断逻辑类型(type)**：字段类型必须映射为以下 5 种之一：`String` (字符串/文本), `Int64` (整数), `Float64` (浮点/数值), `DateTime` (时间/日期), `Boolean` (布尔)。严禁返回原生数据库类型（如 VARCHAR2, NUMBER 等）。
3. **推断业务术语(term)**：对于缺失备注的物理列名，映射为易于理解的中文业务术语。例如 `pue` -> `能效值`。
3. **提取枚举值(enums)**：如果字段描述或 DDL 注释中包含枚举映射（如 0:正常, 1:故障），请解析为 `{"value": 0, "label": "正常"}` 格式。
3. **推断同义词(synonyms)**：为表和字段提供 2-3 个可能的业务同义词，用于增强未来的搜索召回。
4. **生成指标(metrics)**：识别潜在的高价值业务指标及其 SQL 计算逻辑。
5. **识别关系(relationships)**：识别表之间的关联字段和关联类型。

输出必须是严格的 JSON 格式，结构如下：
{
  "tables": [
    {
      "physical_name": "物理表名",
      "term": "业务术语",
      "description": "详细描述",
      "synonyms": ["同义词1", "同义词2"],
      "columns": [
        {
          "physical_name": "物理字段名",
          "term": "业务术语",
          "type": "类型",
          "description": "描述",
          "enums": [{"value": 0, "label": "正常"}],
          "synonyms": ["同义词"],
          "examples": ["示例值"]
        }
      ]
    }
  ],
  "metrics": [
    {
      "name": "指标编码",
      "display_name": "指标名称",
      "description": "描述",
      "calculation_logic": "SQL逻辑",
      "unit": "单位"
    }
  ],
  "relationships": [
    {
      "source_table": "源物理表名",
      "target_table": "目标物理表名",
      "type": "one_to_many",
      "condition": "关联条件",
      "description": "描述"
    }
  ]
}

注意：仅返回 JSON 对象，不要包含 Markdown 代码块标记或任何解释文字。
"""

    @staticmethod
    async def generate_from_content(content: str) -> Dict[str, Any]:
        """
        利用 AI 从文本内容中提取元数据
        """
        messages = [
            {"role": "system", "content": MetadataGeneratorService.SYSTEM_PROMPT},
            {"role": "user", "content": f"请分析以下内容并生成元数据：\n\n{content}"}
        ]
        
        try:
            raw_response = await AIService.chat_completion(messages)
            if not raw_response:
                raise ValueError("AI 返回内容为空")
            
            # 清理潜在的 Markdown 标记
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:-3].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:-3].strip()
                
            result = json.loads(clean_json)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"AI 返回内容解析 JSON 失败: {raw_response}")
            raise ValueError(f"智能解析失败: 返回格式非法")
        except Exception as e:
            logger.error(f"Metadata Generator Error: {e}")
            raise e

    @staticmethod
    async def recommend_metrics(schema_context: str) -> List[Dict[str, Any]]:
        """
        根据给定的表结构上下文，由 AI 推荐高价值业务指标
        """
        system_prompt = """你是一个精通数据分析的 BI 专家。
请分析给定的数据库 Schema（包含表结构、字段含义），推荐 5-10 个**最有业务价值**的分析指标。

指标类型可以是：
1. **聚合型 (KPI)**: 如总数、平均值、比率 (e.g., '能效利用率', '总注册用户')。
2. **维度分布 (Dimension)**: 如按类别分组统计。

输出必须是严格的 JSON 列表格式：
[
  {
    "name": "指标物理名(英文)",
    "display_name": "指标显示名",
    "description": "业务口径描述",
    "calculation_logic": "SQL计算逻辑 (如 avg(pue))",
    "unit": "单位"
  }
]
注意：仅返回 JSON 列表，不要包含 Markdown 标记。
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Schema 定义如下：\n\n{schema_context}"}
        ]
        
        try:
            raw_response = await AIService.chat_completion(messages)
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:-3].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:-3].strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Recommend Metrics Error: {e}")
            return []

    @staticmethod
    async def recommend_relationships(schema_context: str) -> List[Dict[str, Any]]:
        """
        根据给定的表结构上下文，由 AI 推荐表之间的关联关系
        """
        system_prompt = """你是一个专业的数据库架构师。
请分析给定的数据库 Schema（包含表结构、字段含义），推断表之间合理的 JOIN 关联关系。

要求：
1. **识别外键关联**：即使没有物理外键，也要识别逻辑上的主外键关系（如 `user_id` 关联 `users.id`）。
2. **推断关联类型**：识别是 `one_to_many`, `many_to_one` 还是 `one_to_one`。
3. **推断 JOIN 条件**：提供准确的 SQL ON 条件语句。

输出必须是严格的 JSON 列表格式：
[
  {
    "source_table": "源物理表名",
    "target_table": "目标物理表名",
    "type": "LEFT JOIN",
    "condition": "关联条件 (如 t1.user_id = t2.id)",
    "description": "业务含义描述"
  }
]
注意：仅返回 JSON 列表，不要包含 Markdown 标记。
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Schema 定义如下：\n\n{schema_context}"}
        ]
        
        try:
            raw_response = await AIService.chat_completion(messages)
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:-3].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:-3].strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Recommend Relationships Error: {e}")
            return []

    @staticmethod
    async def suggest_description(object_info: Dict[str, Any]) -> str:
        """
        利用 AI 润色或预测业务描述
        """
        system_prompt = """你是一个专业的数据库文案专家。
请根据提供的对象信息（名称、术语、现有上下文），生成一个简洁、专业且富有业务洞察力的【中文描述】。

要求：
1. 字数控制在 20-50 字。
2. 避免技术废话（如“这是一个字段”），直接描述其业务价值。
3. 如果是表，描述其核心存储内容和业务用途。
4. 如果是字段，描述其物理含义和在业务分析中的作用。

仅返回生成的描述字符串，不要包含任何其他前导词或引号。
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"对象信息如下：\n{json.dumps(object_info, ensure_ascii=False)}"}
        ]
        
        try:
            return await AIService.chat_completion(messages)
        except Exception:
            return ""

    @staticmethod
    async def batch_enrich(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量为表和字段生成元数据建议 (术语和描述)
        """
        system_prompt = """你是一个专业的元数据管理专家。
我会为你提供一组数据库表和字段的物理名称。请利用你的知识储备，为每个项推断出最合适的：
1. **term**: 中文业务术语 (简洁有力，如 'pue' -> '能效值', 'create_time' -> '创建时间')。
2. **description**: 业务描述 (专业且有洞察力，20字左右)。

输入格式：[{"type": "table|column", "name": "物理名", "context": "上下文信息"}]
输出格式：严格的 JSON 列表，顺序必须与输入一致：
[{"term": "...", "description": "..."}]

仅返回 JSON 列表，不要包含 Markdown 代码块或解释。
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"需要预测的对象列表：\n{json.dumps(items, ensure_ascii=False)}"}
        ]
        
        try:
            raw_response = await AIService.chat_completion(messages)
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:-3].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:-3].strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Batch Enrich Error: {e}")
            return []