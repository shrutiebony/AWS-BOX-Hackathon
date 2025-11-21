# Quick Start - Box MCP Server

## 🚀 Setup Complete!

The Box MCP server has been installed and configured. You just need to add your Box credentials.

## ⚡ Quick Configuration (2 minutes)

1. **Get Box Credentials**:
   - Visit: https://app.box.com/developers/console
   - Create a new "Custom App" → "User Authentication (OAuth 2.0)"
   - Add redirect URI: `http://localhost:8000/callback`
   - Copy your **Client ID** and **Client Secret**

2. **Configure .env file**:
   ```bash
   cd /Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box
   cp .env.example .env
   # Edit .env and add your BOX_CLIENT_ID and BOX_CLIENT_SECRET
   ```

3. **Restart Cursor** and you're ready to go!

## 🧪 Test It

In Cursor AI chat, try:
- "List my Box files"
- "Search for documents in Box"
- "What's in my Box account?"

## 📖 Full Guide

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions and troubleshooting.

