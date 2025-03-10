import os
import json
import requests
from collections.abc import Generator
from typing import Any, Dict, Optional, List

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class KnowledgeRetrieveTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # 获取参数
        dataset_id = tool_parameters.get('dataset_id')
        query = tool_parameters.get('query')
        search_method = tool_parameters.get('search_method', 'semantic_search')
        reranking_enable = tool_parameters.get('reranking_enable', False)
        top_k = tool_parameters.get('top_k', 3)
        score_threshold_enabled = tool_parameters.get('score_threshold_enabled', False)
        score_threshold = tool_parameters.get('score_threshold', 0.5)
        
        # 调试信息
        print(f"接收到的参数: {tool_parameters}")
        
        # 检查必要参数
        if not dataset_id:
            yield self.create_text_message("知识库ID是必需的。")
            return
        
        if not query:
            yield self.create_text_message("查询内容是必需的。")
            return
        
        # 从环境变量获取API Key
        api_key = os.environ.get('DIFY_KNOWLEDGE_API_KEY')
        if not api_key:
            yield self.create_text_message("未找到API Key。请确保在插件配置中设置了它。")
            return
        
        # 设置请求头
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构建检索模型参数
        retrieval_model = {
            "search_method": search_method,
            "reranking_enable": reranking_enable,
            "reranking_mode": None,
            "reranking_model": {
                "reranking_provider_name": "",
                "reranking_model_name": ""
            },
            "weights": None,
            "top_k": top_k,
            "score_threshold_enabled": score_threshold_enabled,
            "score_threshold": score_threshold if score_threshold_enabled else None
        }
        
        # 执行知识库检索
        yield self.create_text_message(f"正在从知识库 {dataset_id} 检索与 '{query}' 相关的信息...")
        
        result = self._retrieve_from_knowledge_base(headers, dataset_id, query, retrieval_model)
        if not result:
            yield self.create_text_message("检索失败。请检查您的API Key和参数。")
            return
        
        if isinstance(result, str):
            # 这是一个错误消息
            yield self.create_text_message(f"错误: {result}")
            return
            
        records = result.get('records', [])
        
        if not records:
            yield self.create_text_message(f"未找到与 '{query}' 相关的信息。")
            return
        
        # 返回检索结果
        yield self.create_text_message(f"找到 {len(records)} 条相关信息:")
        
        for i, record in enumerate(records):
            segment = record.get('segment', {})
            content = segment.get('content', '')
            document = segment.get('document', {})
            document_name = document.get('name', '未知文档')
            score = record.get('score', 0)
            
            result_text = f"结果 {i+1}:\n"
            result_text += f"文档: {document_name}\n"
            result_text += f"相关度: {score}\n"
            result_text += f"内容: {content}\n"
            result_text += "-------------------"
            
            yield self.create_text_message(result_text)
        
        # 返回详细信息
        yield self.create_json_message({
            "status": "success",
            "query": query,
            "knowledge_base_id": dataset_id,
            "results": records
        })
    
    def _retrieve_from_knowledge_base(self, headers: Dict, dataset_id: str, query: str, retrieval_model: Dict) -> Optional[Dict]:
        """从知识库检索信息"""
        try:
            url = f"https://api.dify.ai/v1/datasets/{dataset_id}/retrieve"
            
            payload = {
                "query": query,
                "retrieval_model": retrieval_model
            }
            
            print(f"知识库检索请求URL: {url}")
            print(f"知识库检索请求参数: {payload}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"知识库检索响应状态码: {response.status_code}")
            print(f"知识库检索响应内容: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                error_code = error_data.get('code', 'unknown_error')
                error_message = error_data.get('message', '未知错误')
                
                if error_code == "dataset_not_found":
                    return "知识库不存在或无权访问"
                elif error_code == "invalid_api_key":
                    return "API Key无效"
                else:
                    print(f"检索知识库时出错: {error_message}")
                    print(f"状态码: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    return f"检索失败: {error_message}"
        except Exception as e:
            print(f"检索知识库时发生错误: {str(e)}")
            return f"发生异常: {str(e)}" 