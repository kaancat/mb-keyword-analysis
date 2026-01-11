# Google Ads RAG Knowledge MCP Server

This MCP server provides semantic search access to the Monday Brew Google Ads knowledge base.

## Tools

- `query_knowledge(query, n_results, filter_type)`: General semantic search.
- `get_methodology(task_type)`: Get specific methodology for tasks like keyword research.
- `list_examples()`: List available case studies.
- `get_example(client_name)`: Get details for a specific case study.

## Resources

- `rag://stats`: View knowledge base statistics.

## Installation

1. Ensure you have `uv` installed.
2. Add to your Claude Desktop or Cursor configuration:

```json
{
  "mcpServers": {
    "google-ads-rag": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/kaancatalkaya/Desktop/Projects/Google Ads - mondaybrew/mcp-servers/google-ads-rag", "python", "server.py"],
      "env": {
        "OPENAI_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```
