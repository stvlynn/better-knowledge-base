from typing import Any
import requests
import os

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class KnowledgeProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials.get('api_key')
            if not api_key:
                raise ValueError("API Key is required")
            
            # 将API Key保存到环境变量中，以便工具可以访问
            os.environ['DIFY_KNOWLEDGE_API_KEY'] = api_key
            
            # 尝试使用API Key获取知识库列表，验证API Key是否有效
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get('https://api.dify.ai/v1/datasets?page=1&limit=1', headers=headers)
            
            if response.status_code != 200:
                error_data = response.json()
                raise ValueError(f"API Key validation failed: {error_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
