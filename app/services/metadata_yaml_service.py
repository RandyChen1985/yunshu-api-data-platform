import yaml
from typing import Dict, Any, List

class MetadataYamlService:
    """
    元数据序列化服务
    将元数据结构转化为 LLM 友好的 YAML 格式
    """

    @staticmethod
    def generate_dataset_yaml(dataset: Dict[str, Any]) -> str:
        """
        生成整个数据集的语义上下文 YAML
        """
        output = {
            "dataset_name": dataset.get('display_name') or dataset.get('name'),
            "domain_description": dataset.get('description', ''),
            "data_source": dataset.get('data_source'),
            "entities": []
        }

        # 1. 构建表和字段
        for table in dataset.get('tables', []):
            tbl_info = {
                "name": table['physical_name'],
                "term": table['term'],
                "desc": table.get('description', ''),
                "synonyms": table.get('synonyms', []),
                "columns": []
            }
            
            for col in table.get('columns', []):
                col_info = {
                    "name": col['physical_name'],
                    "term": col['term'],
                    "type": col.get('type'),
                    "desc": col.get('description', '')
                }
                if col.get('enums'):
                    col_info["enums"] = col['enums']
                if col.get('is_primary'):
                    col_info["pk"] = True
                
                tbl_info["columns"].append(col_info)
            
            output["entities"].append(tbl_info)

        # 2. 注入指标
        if dataset.get('metrics'):
            output["business_metrics"] = []
            for m in dataset['metrics']:
                output["business_metrics"].append({
                    "name": m['display_name'],
                    "logic": m['calculation_logic'],
                    "desc": m.get('description', '')
                })

        # 3. 注入关联关系
        if dataset.get('relationships'):
            output["relationships"] = []
            for r in dataset['relationships']:
                output["relationships"].append({
                    "source": r['source_table'],
                    "target": r['target_table'],
                    "condition": r['join_condition'],
                    "type": r.get('join_type', 'LEFT JOIN')
                })

        return yaml.dump(output, allow_unicode=True, sort_keys=False)

    @staticmethod
    def combine_yamls(yaml_list: List[str]) -> str:
        """
        将多个 YAML 片段合并为一个完整的展示文档
        """
        if not yaml_list:
            return ""
        
        separator = "\n" + "-"*40 + "\n"
        return separator.join(yaml_list)

    @staticmethod
    def generate_table_yaml(table: Dict[str, Any]) -> str:
        """
        生成单张表的语义上下文 YAML
        """
        tbl_info = {
            "entity": {
                "name": table['physical_name'],
                "term": table['term'],
                "desc": table.get('description', ''),
                "synonyms": table.get('synonyms', []),
                "columns": []
            }
        }
        
        for col in table.get('columns', []):
            col_info = {
                "name": col['physical_name'],
                "term": col['term'],
                "type": col.get('type'),
                "desc": col.get('description', '')
            }
            if col.get('enums'):
                col_info["enums"] = col['enums']
            if col.get('is_primary'):
                col_info["pk"] = True
            
            tbl_info["entity"]["columns"].append(col_info)
            
        return yaml.dump(tbl_info, allow_unicode=True, sort_keys=False)

    @staticmethod
    def generate_metric_yaml(metric: Dict[str, Any]) -> str:
        """
        生成单个指标的语义上下文 YAML
        """
        metric_info = {
            "metric": {
                "name": metric['name'],
                "display_name": metric['display_name'],
                "logic": metric['calculation_logic'],
                "desc": metric.get('description', ''),
                "unit": metric.get('unit', '')
            }
        }
        return yaml.dump(metric_info, allow_unicode=True, sort_keys=False)
