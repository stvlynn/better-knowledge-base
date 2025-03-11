import os
import json
import time
import requests

# Test parameters
knowledge_base_name = "Test KB"
description = ""
document_name = "Test Doc"
text_content = "This is a test content for the document."
permission = "only_me"
indexing_technique = "high_quality"

# Set API Key
api_key = "test_key"  # Replace with your actual API Key

# Set request headers
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("Starting API request test...")

# Step 1: Create knowledge base
print("Step 1: Creating knowledge base")
url = "https://api.dify.ai/v1/datasets"
payload = {
    "name": knowledge_base_name,
    "description": description,
    "permission": permission,
    "indexing_technique": indexing_technique,
    "provider": "vendor"
}

print(f"Request URL: {url}")
print(f"Request parameters: {payload}")

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        dataset_id = result.get('id')
        print(f"Knowledge base created successfully, ID: {dataset_id}")
        
        # Step 2: Create document by text
        print("\nStep 2: Creating document")
        url = f"https://api.dify.ai/v1/datasets/{dataset_id}/document/create-by-text"
        
        # Prepare processing rules
        process_rule = {
            "mode": "automatic"
        }
        
        payload = {
            "name": document_name,
            "text": text_content,
            "indexing_technique": indexing_technique,
            "process_rule": process_rule
        }
        
        print(f"Request URL: {url}")
        print(f"Request parameters: {payload}")
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            document = result.get('document', {})
            document_id = document.get('id')
            batch = result.get('batch', '')
            print(f"Document created successfully, ID: {document_id}, Batch: {batch}")
            
            # Step 3: Check document processing status
            print("\nStep 3: Checking document processing status")
            url = f"https://api.dify.ai/v1/datasets/{dataset_id}/documents/{batch}/indexing-status"
            
            print(f"Request URL: {url}")
            
            response = requests.get(url, headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                documents = result.get('data', [])
                if documents:
                    document = documents[0]
                    status = document.get('indexing_status', 'unknown')
                    print(f"Document status: {status}")
                    
                    # 测试输出JSON响应
                    print("\nStep 4: 输出最终JSON响应")
                    final_response = {
                        "status": "success",
                        "knowledge_base_id": dataset_id,  # 单独列出知识库ID作为顶级字段
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
                    }
                    print(f"最终JSON响应: {json.dumps(final_response, indent=2)}")
                    print(f"知识库ID: {final_response['knowledge_base_id']}")
                else:
                    print("No document status information found")
            else:
                error_data = response.json()
                error_code = error_data.get('code', 'unknown_error')
                error_message = error_data.get('message', 'Unknown error')
                
                if error_code == "archived_document_immutable":
                    print("Error: The archived document is not editable.")
                elif error_code == "document_already_finished":
                    print("Error: The document has been processed. Please refresh the page or go to the document details.")
                elif error_code == "document_indexing":
                    print("Error: The document is being processed and cannot be edited.")
                else:
                    print(f"Error checking document status: {error_message}")
        else:
            error_data = response.json()
            error_code = error_data.get('code', 'unknown_error')
            error_message = error_data.get('message', 'Unknown error')
            
            if error_code == "no_file_uploaded":
                print("Error: Please upload your file.")
            elif error_code == "too_many_files":
                print("Error: Only one file is allowed.")
            elif error_code == "file_too_large":
                print("Error: File size exceeded.")
            elif error_code == "unsupported_file_type":
                print("Error: File type not allowed.")
            elif error_code == "high_quality_dataset_only":
                print("Error: Current operation only supports 'high-quality' datasets.")
            elif error_code == "dataset_not_initialized":
                print("Error: The dataset is still being initialized or indexing. Please wait a moment.")
            elif error_code == "invalid_metadata":
                print("Error: The metadata content is incorrect. Please check and verify.")
            else:
                print(f"Error creating document: {error_message}")
    else:
        error_data = response.json()
        error_code = error_data.get('code', 'unknown_error')
        error_message = error_data.get('message', 'Unknown error')
        
        if error_code == "dataset_name_duplicate":
            print("Error: The dataset name already exists. Please modify your dataset name.")
        elif error_code == "invalid_action":
            print("Error: Invalid action.")
        else:
            print(f"Error creating knowledge base: {error_message}")
except Exception as e:
    print(f"Error occurred during test: {str(e)}")

print("Test completed")

def test_knowledge_upload_tool():
    """Test the KnowledgeUploadTool with the modified output"""
    from tools.knowledge_upload import KnowledgeUploadTool
    from dify_plugin.entities.tool import ToolInvokeMessage
    from unittest.mock import MagicMock, patch
    
    print("\n=== Testing KnowledgeUploadTool with modified output ===")
    
    # Create mock objects for runtime and session
    mock_runtime = MagicMock()
    mock_session = MagicMock()
    
    # Create tool instance with mock objects
    tool = KnowledgeUploadTool(mock_runtime, mock_session)
    
    # Set test parameters
    tool_parameters = {
        "knowledge_base_name": "Test KB",
        "description": "Test description",
        "document_name": "Test Doc",
        "text": "This is a test content for the document.",
        "permission": "only_me",
        "indexing_technique": "high_quality"
    }
    
    # Mock the API calls
    tool._create_knowledge_base = lambda headers, name, desc, perm, tech: "test-dataset-id-123"
    tool._create_document_by_text = lambda headers, dataset_id, doc_name, text, tech: {"id": "test-doc-id-456", "batch": "test-batch-789"}
    tool._check_document_status = lambda headers, dataset_id, batch: "completed"
    
    # Mock the create_text_message and create_json_message methods
    def mock_create_text_message(content):
        mock_msg = MagicMock()
        mock_msg.message_type = "text"
        mock_msg.content = content
        return mock_msg
    
    def mock_create_json_message(content):
        mock_msg = MagicMock()
        mock_msg.message_type = "json"
        mock_msg.content = json.dumps(content)
        return mock_msg
    
    tool.create_text_message = mock_create_text_message
    tool.create_json_message = mock_create_json_message
    
    # Mock environment variable for API key
    with patch.dict('os.environ', {'DIFY_KNOWLEDGE_API_KEY': 'test_api_key'}):
        # Invoke the tool
        messages = list(tool._invoke(tool_parameters))
        
        # Print all messages
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg.message_type}")
            if msg.message_type == "json":
                json_content = json.loads(msg.content)
                print(f"JSON content: {json.dumps(json_content, indent=2)}")
                
                # Verify the output fields
                assert "id" in json_content, "Missing 'id' field in output"
                assert "status" in json_content, "Missing 'status' field in output"
                assert json_content["status"] == 200, "Status should be 200"
                assert json_content["id"] == "test-dataset-id-123", "ID should match the test dataset ID"
                
                print("✅ Output validation passed!")
            else:
                print(f"Content: {msg.content}")
    
    print("=== Test completed ===\n")

if __name__ == "__main__":
    # Run the new test for the modified output
    test_knowledge_upload_tool()
    
    # Uncomment to run the original API test
    # try:
    #     # Step 1: Create knowledge base
    #     # ... existing code ...
    # except Exception as e:
    #     print(f"Error occurred during test: {str(e)}")
    # 
    # print("Test completed") 