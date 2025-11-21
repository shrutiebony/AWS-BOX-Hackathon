# How to Use Box MCP Server in Cursor

## ✅ Your Box MCP Server is Configured!

The Box MCP server is set up and ready to use. Here's how to access your Box files:

## 🎯 Method 1: Use Cursor's AI Chat (Recommended)

1. **Open Cursor's AI Chat**:
   - Click the chat icon in Cursor's sidebar
   - Or use the keyboard shortcut (usually `Cmd+L` or `Cmd+K`)

2. **Ask to list your Box files**:
   - Type: `"List my Box files"`
   - Or: `"Show me what's in my Box account"`
   - Or: `"What files do I have in Box?"`

3. **First-time authentication**:
   - When you first use Box features, Cursor will open your browser
   - You'll be asked to authorize the Box app
   - Click "Authorize" to grant permissions
   - You'll be redirected back to Cursor

## 🔍 Method 2: Check MCP Server Status

If the MCP server isn't working in chat, check:

1. **Verify Cursor has restarted** after configuration
2. **Check MCP server configuration**:
   ```bash
   cat ~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   ```

3. **Test the server manually**:
   ```bash
   cd /Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box
   uv run src/mcp_server_box.py
   ```
   The server should start without errors.

## 📋 Available Box Commands in Cursor Chat

Once the MCP server is working, you can use these commands:

- **List files**: "List my Box files"
- **Search**: "Search for documents in Box"
- **Read files**: "Read the file [filename] from Box"
- **Upload**: "Upload [file] to Box"
- **Folder info**: "Show me what's in the [folder name] folder"
- **Create folder**: "Create a folder called [name] in Box"

## 🆘 Troubleshooting

### MCP Server Not Working in Chat

1. **Restart Cursor completely** (quit and reopen)
2. **Check the .env file** has correct credentials:
   ```bash
   cd /Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box
   cat .env
   ```
3. **Verify Box app configuration**:
   - Redirect URI `http://localhost:8000/callback` is set in Box Developer Console
   - App is authorized (if required)

### Authentication Issues

- If OAuth fails, check that your Box app redirect URI matches
- You may need to re-authorize if tokens expire
- Check Box Developer Console for app status

## 💡 Note

The MCP server is designed to work through Cursor's AI chat interface, not through direct agent commands. This is by design - it allows Cursor's AI to securely access your Box account with proper authentication.

---

**Ready to use?** Open Cursor's chat and ask: "List my Box files" 🚀

