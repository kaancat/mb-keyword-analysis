# mb-keyword-analysis

Complete Google Ads keyword analysis system for Claude Code. Self-contained plugin with everything needed to run keyword analysis workflows from any project.

## Installation

```bash
/plugin install mb-keyword-analysis@mb-plugins
```

## First-Time Setup

After installing, you need to set up the MCP RAG server:

### 1. Clone the plugin for local setup

```bash
git clone https://github.com/kaancat/mb-keyword-analysis.git ~/Desktop/Plugins/mb-keyword-analysis
cd ~/Desktop/Plugins/mb-keyword-analysis
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env with your Google Ads API credentials
```

### 3. Install dependencies and build RAG database

```bash
cd mcp-servers/google-ads-rag
pip install -e .
cd ../..
python scripts/build_rag_db.py
```

This builds the ChromaDB from the knowledge base files (transcripts, methodology, examples).

### 4. Configure MCP server in Claude

Add to your Claude settings (`~/.claude/settings.json` or project settings):

```json
{
  "mcpServers": {
    "google-ads-rag": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "~/Desktop/Plugins/mb-keyword-analysis/mcp-servers/google-ads-rag"
    }
  }
}
```

## Usage

```bash
/keyword-analysis
```

## What's Included

- **Commands** - `/keyword-analysis` workflow with phase gates
- **Skills** - Decision trees, templates, examples
- **Hooks** - Phase gate validation
- **MCP Server** - Google Ads RAG with methodology and case studies
- **API Connectors** - Keyword Planner, Google Sheets, Search Console, GA4, GTM, BigQuery
- **Knowledge Base** - Methodology, transcripts, examples, best practices
- **Schemas** - Deliverable formats (keyword analysis, campaign structure, ad copy, ROI calculator)
- **Scripts** - Utilities including ROI tab generator

## Rebuilding the RAG Database

If you add new content to `knowledge_base/`, rebuild:

```bash
python scripts/build_rag_db.py
```

## Development

Edit files, bump version in `.claude-plugin/plugin.json`, push to GitHub, then:

```bash
/plugin update mb-keyword-analysis@mb-plugins
```

Also update the version in `mb-marketplace` if needed.
