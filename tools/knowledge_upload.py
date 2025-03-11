import os
import json
import time
import requests
from collections.abc import Generator
from typing import Any, Dict, Optional, List

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class KnowledgeUploadTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get parameters
        knowledge_base_name = tool_parameters.get('knowledge_base_name')
        description = tool_parameters.get('description', '')
        document_name = tool_parameters.get('document_name')
        text_content = tool_parameters.get('text')
        permission = tool_parameters.get('permission', 'only_me')
        indexing_technique = tool_parameters.get('indexing_technique', 'high_quality')
        
        # Debug information
        print(f"Received parameters: {tool_parameters}")
        print(f"Text content: {text_content}")
        
        # Check required parameters
        if not knowledge_base_name:
            yield self.create_text_message("Knowledge base name is required.")
            return
        
        if not document_name:
            yield self.create_text_message("Document name is required.")
            return
        
        if not text_content:
            yield self.create_text_message("Text content is required.")
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
        
        # Step 1: Create knowledge base
        yield self.create_text_message(f"Creating knowledge base: {knowledge_base_name}...")
        
        dataset_id = self._create_knowledge_base(headers, knowledge_base_name, description, permission, indexing_technique)
        if not dataset_id:
            yield self.create_text_message("Failed to create knowledge base. Please check your API Key and parameters.")
            return
        
        yield self.create_text_message(f"Knowledge base created successfully, ID: {dataset_id}")
        
        # Step 2: Create document with text
        yield self.create_text_message(f"Creating document: {document_name}...")
        
        document_result = self._create_document_by_text(headers, dataset_id, document_name, text_content, indexing_technique)
        if not document_result:
            yield self.create_text_message("Failed to create document. Please check your parameters.")
            return
        
        if isinstance(document_result, str):
            # This is an error message
            yield self.create_text_message(f"Error: {document_result}")
            return
            
        document_id = document_result.get('id')
        batch = document_result.get('batch')
        
        yield self.create_text_message(f"Document created successfully, ID: {document_id}, Batch: {batch}")
        
        # Step 3: Check document processing status
        yield self.create_text_message(f"Processing document, please wait...")
        
        status_result = self._check_document_status(headers, dataset_id, batch)
        
        if isinstance(status_result, str) and status_result.startswith("Error:"):
            yield self.create_text_message(status_result)
            return
            
        status = status_result
        
        if status == "completed":
            yield self.create_text_message(f"Document processing completed!")
        elif status == "error" or status == "failed":
            yield self.create_text_message(f"Document processing failed. Please check your text content.")
        else:
            yield self.create_text_message(f"Document is being processed, current status: {status}")
            yield self.create_text_message(f"You can check the result later on the Dify platform.")
        
        # Return detailed information
        yield self.create_json_message({
            "status": 200,
            "id": dataset_id,
            "knowledge_base": {
                "id": dataset_id,
                "name": knowledge_base_name
            },
            "document": {
                "id": document_id,
                "name": document_name,
                "batch": batch,
                "status": status
            }
        })
    
    def _create_knowledge_base(self, headers: Dict, name: str, description: str, permission: str, indexing_technique: str) -> Optional[str]:
        """Create an empty knowledge base"""
        try:
            url = "https://api.dify.ai/v1/datasets"
            payload = {
                "name": name,
                "description": description,
                "permission": permission,
                "indexing_technique": indexing_technique,
                "provider": "vendor"
            }
            
            print(f"Knowledge base creation request URL: {url}")
            print(f"Knowledge base creation request parameters: {payload}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"Knowledge base creation response status code: {response.status_code}")
            print(f"Knowledge base creation response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return result.get('id')
            else:
                error_data = response.json()
                error_code = error_data.get('code', 'unknown_error')
                error_message = error_data.get('message', 'Unknown error')
                
                if error_code == "dataset_name_duplicate":
                    print(f"Error: The dataset name already exists. Please modify your dataset name.")
                elif error_code == "invalid_action":
                    print(f"Error: Invalid action.")
                else:
                    print(f"Error creating knowledge base: {error_message}")
                    
                print(f"Status code: {response.status_code}")
                print(f"Response content: {response.text}")
                return None
        except Exception as e:
            print(f"Error occurred while creating knowledge base: {str(e)}")
            return None
    
    def _create_document_by_text(self, headers: Dict, dataset_id: str, document_name: str, text_content: str, indexing_technique: str) -> Optional[Dict]:
        """Create document by text"""
        try:
            # Correct API endpoint
            url = f"https://api.dify.ai/v1/datasets/{dataset_id}/document/create-by-text"
            
            # Prepare processing rules
            process_rule = {
                "mode": "automatic"
            }
            
            # Ensure text content is a string
            if not isinstance(text_content, str):
                text_content = str(text_content)
            
            payload = {
                "name": document_name,
                "text": text_content,
                "indexing_technique": indexing_technique,
                "process_rule": process_rule
            }
            
            print(f"Document creation request URL: {url}")
            print(f"Document creation request parameters: {payload}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"Document creation response status code: {response.status_code}")
            print(f"Document creation response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                document = result.get('document', {})
                batch = result.get('batch', '')
                return {
                    'id': document.get('id'),
                    'batch': batch
                }
            else:
                error_data = response.json()
                error_code = error_data.get('code', 'unknown_error')
                error_message = error_data.get('message', 'Unknown error')
                
                if error_code == "no_file_uploaded":
                    return "Error: Please upload your file."
                elif error_code == "too_many_files":
                    return "Error: Only one file is allowed."
                elif error_code == "file_too_large":
                    return "Error: File size exceeded."
                elif error_code == "unsupported_file_type":
                    return "Error: File type not allowed."
                elif error_code == "high_quality_dataset_only":
                    return "Error: Current operation only supports 'high-quality' datasets."
                elif error_code == "dataset_not_initialized":
                    return "Error: The dataset is still being initialized or indexing. Please wait a moment."
                elif error_code == "invalid_metadata":
                    return "Error: The metadata content is incorrect. Please check and verify."
                else:
                    print(f"Error creating document: {error_message}")
                    print(f"Status code: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return None
        except Exception as e:
            print(f"Error occurred while creating document: {str(e)}")
            print(f"Exception details: {repr(e)}")
            return None
    
    def _check_document_status(self, headers: Dict, dataset_id: str, batch: str) -> str:
        """Check document processing status"""
        try:
            # Use the correct API endpoint
            url = f"https://api.dify.ai/v1/datasets/{dataset_id}/documents/{batch}/indexing-status"
            
            print(f"Document status check request URL: {url}")
            
            # Try to check status, maximum 5 attempts
            for i in range(5):
                print(f"Document status check attempt {i+1}")
                response = requests.get(url, headers=headers)
                
                print(f"Document status check response status code: {response.status_code}")
                print(f"Document status check response content: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    documents = result.get('data', [])
                    
                    if documents:
                        document = documents[0]
                        status = document.get('indexing_status', 'unknown')
                        print(f"Document status: {status}")
                        
                        if status in ['completed', 'error', 'failed']:
                            return status
                    
                    # If still processing, wait 3 seconds before checking again
                    print("Document is still being processed, waiting 3 seconds before checking again")
                    time.sleep(3)
                else:
                    error_data = response.json()
                    error_code = error_data.get('code', 'unknown_error')
                    error_message = error_data.get('message', 'Unknown error')
                    
                    if error_code == "archived_document_immutable":
                        return "Error: The archived document is not editable."
                    elif error_code == "document_already_finished":
                        return "Error: The document has been processed. Please refresh the page or go to the document details."
                    elif error_code == "document_indexing":
                        return "Error: The document is being processed and cannot be edited."
                    else:
                        print(f"Error checking document status: {error_message}")
                        print(f"Response content: {response.text}")
                        return "Error: Failed to check document status."
            
            # If still not completed after 5 attempts, return processing status
            return "processing"
        except Exception as e:
            print(f"Error occurred while checking document status: {str(e)}")
            return "Error: An unexpected error occurred while checking document status." 