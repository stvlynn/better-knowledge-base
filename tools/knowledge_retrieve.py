import os
import json
import requests
from collections.abc import Generator
from typing import Any, Dict, Optional, List

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class KnowledgeRetrieveTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get parameters
        dataset_id = tool_parameters.get('dataset_id')
        query = tool_parameters.get('query')
        search_method = tool_parameters.get('search_method', 'semantic_search')
        reranking_enable = tool_parameters.get('reranking_enable', False)
        top_k = tool_parameters.get('top_k', 3)
        score_threshold_enabled = tool_parameters.get('score_threshold_enabled', False)
        score_threshold = tool_parameters.get('score_threshold', 0.5)
        
        # Debug information
        print(f"Received parameters: {tool_parameters}")
        
        # Check required parameters
        if not dataset_id:
            yield self.create_text_message("Knowledge base ID is required.")
            return
        
        if not query:
            yield self.create_text_message("Query content is required.")
            return
        
        # Get API Key from environment variables
        api_key = os.environ.get('DIFY_KNOWLEDGE_API_KEY')
        if not api_key:
            yield self.create_text_message("API Key not found. Please make sure it's set in the plugin configuration.")
            return
        
        # Set request headers
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Build retrieval model parameters
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
        
        # Perform knowledge base retrieval
        yield self.create_text_message(f"Retrieving information from knowledge base {dataset_id} related to '{query}'...")
        
        result = self._retrieve_from_knowledge_base(headers, dataset_id, query, retrieval_model)
        if not result:
            yield self.create_text_message("Retrieval failed. Please check your API Key and parameters.")
            return
        
        if isinstance(result, str):
            # This is an error message
            yield self.create_text_message(f"Error: {result}")
            return
            
        records = result.get('records', [])
        
        if not records:
            yield self.create_text_message(f"No information found related to '{query}'.")
            return
        
        # Return retrieval results
        yield self.create_text_message(f"Found {len(records)} related results:")
        
        for i, record in enumerate(records):
            segment = record.get('segment', {})
            content = segment.get('content', '')
            document = segment.get('document', {})
            document_name = document.get('name', 'Unknown document')
            score = record.get('score', 0)
            
            result_text = f"Result {i+1}:\n"
            result_text += f"Document: {document_name}\n"
            result_text += f"Relevance: {score}\n"
            result_text += f"Content: {content}\n"
            result_text += "-------------------"
            
            yield self.create_text_message(result_text)
        
        # Return detailed information
        yield self.create_json_message({
            "status": "success",
            "query": query,
            "knowledge_base_id": dataset_id,
            "results": records
        })
    
    def _retrieve_from_knowledge_base(self, headers: Dict, dataset_id: str, query: str, retrieval_model: Dict) -> Optional[Dict]:
        """Retrieve information from knowledge base"""
        try:
            url = f"https://api.dify.ai/v1/datasets/{dataset_id}/retrieve"
            
            payload = {
                "query": query,
                "retrieval_model": retrieval_model
            }
            
            print(f"Knowledge base retrieval request URL: {url}")
            print(f"Knowledge base retrieval request parameters: {payload}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"Knowledge base retrieval response status code: {response.status_code}")
            print(f"Knowledge base retrieval response content: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                error_code = error_data.get('code', 'unknown_error')
                error_message = error_data.get('message', 'Unknown error')
                
                if error_code == "dataset_not_found":
                    return "Knowledge base does not exist or you don't have access"
                elif error_code == "invalid_api_key":
                    return "Invalid API Key"
                else:
                    print(f"Error retrieving from knowledge base: {error_message}")
                    print(f"Status code: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return f"Retrieval failed: {error_message}"
        except Exception as e:
            print(f"Error occurred while retrieving from knowledge base: {str(e)}")
            return f"Exception occurred: {str(e)}" 