# Dify Knowledge Base Manager Plugin

A plugin for managing Dify knowledge base - creating knowledge bases, uploading text content, and retrieving information.

## Features

- One-click creation of new knowledge bases and text content upload
- Support for direct text content upload to Dify knowledge base
- Support for selecting indexing technology (high quality or economy mode)
- Support for setting knowledge base permissions (only me or publicly readable)
- Provides upload status and result feedback
- Retrieves information from knowledge base using various search methods
- Support for keyword search, semantic search, full-text search, and hybrid search
- Support for result reranking and score threshold filtering
- Returns knowledge base ID as output variable for further operations

## Prerequisites

Before using this plugin, you need:

1. A Dify platform account
2. Knowledge base API Key

## How to Get API Key

1. Log in to the Dify platform
2. Navigate to the knowledge base page
3. Switch to the **API Access** page from the left navigation
4. Manage access credentials in the **API Keys** section

## How to Get Knowledge Base ID

The knowledge base ID can be obtained from the knowledge base URL, for example:
`https://app.dify.ai/datasets/12345678-1234-1234-1234-123456789012`
where `12345678-1234-1234-1234-123456789012` is the knowledge base ID.

## Upload Tool Parameters

- **Knowledge Base Name**: The name of the knowledge base to create
- **Description**: Description of the knowledge base (optional)
- **Document Name**: The name of the document to create
- **Text Content**: The text content to upload
- **Permission**: Knowledge base permission settings
  - only_me: Only the creator can access
  - publicly_readable: Everyone can read
- **Indexing Technology**: Choose high_quality or economy mode

## Retrieve Tool Parameters

- **Knowledge Base ID**: The ID of the knowledge base to retrieve from (required)
- **Query**: The query to search for in the knowledge base (required)
- **Search Method**: The method to use for searching the knowledge base (optional, default is semantic search)
  - keyword_search: Keyword search, based on keyword matching
  - semantic_search: Semantic search, based on semantic understanding
  - full_text_search: Full text search, searches the entire text content
  - hybrid_search: Hybrid search, combines keyword and semantic search
- **Enable Reranking**: Whether to enable reranking of search results (optional, default is false)
- **Number of Results**: The number of results to return (optional, default is 3)
- **Enable Score Threshold**: Whether to enable score threshold filtering (optional, default is false)
- **Score Threshold**: The minimum score threshold for results (0-1) (optional, default is 0.5)

## Upload Workflow

1. Create a new knowledge base
2. Create a document with text
3. Query document processing status
4. Return processing results and knowledge base ID

## Retrieve Workflow

1. Provide knowledge base ID and query content
2. Select search method and other parameters
3. Execute knowledge base retrieval
4. Return retrieval results and related information

## Upload Output

The upload tool returns a JSON response with the following structure:
```json
{
  "status": "success",
  "knowledge_base_id": "12345678-1234-1234-1234-123456789012",
  "knowledge_base": {
    "id": "12345678-1234-1234-1234-123456789012",
    "name": "Knowledge Base Name"
  },
  "document": {
    "id": "document-id",
    "name": "Document Name",
    "batch": "batch-id",
    "status": "completed"
  }
}
```

## Retrieve Output

The retrieve tool returns a JSON response with the following structure:
```json
{
  "status": "success",
  "query": "Query content",
  "knowledge_base_id": "Knowledge base ID",
  "results": [
    {
      "segment": {
        "id": "Segment ID",
        "content": "Segment content",
        "document": {
          "id": "Document ID",
          "name": "Document name"
        }
      },
      "score": 0.95
    }
  ]
}
```

The `knowledge_base_id` field can be used for further operations with the knowledge base.

## Notes

- Text content requires some time for processing and indexing after upload
- Processing large amounts of text may take longer
- If processing is not complete, the plugin will return the current status, and you can check the processing results later on the Dify platform
- Text content will be automatically segmented for processing, using automatic mode by default

## Error Handling

The plugin handles various error scenarios including:
- Invalid API keys
- Duplicate knowledge base names
- File size limitations
- Unsupported file types
- Processing status errors
- Knowledge base not found or no access
- Query parameter errors

## knowledge-manager

**Author:** stvlynn
**Version:** 0.0.1
**Type:** tool

### Description

A tool for managing Dify knowledge base - creating knowledge bases, uploading text content, and retrieving information.

## 支持的文件格式

- 文本文件 (.txt)
- PDF文件 (.pdf)
- Word文档 (.doc, .docx)
- Markdown文件 (.md, .markdown)
- HTML文件 (.html, .htm)
- Excel文件 (.xlsx)
- CSV文件 (.csv)



