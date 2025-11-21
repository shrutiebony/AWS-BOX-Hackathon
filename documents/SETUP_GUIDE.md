# Box MCP Server Setup Guide for Cursor AI

This guide will help you set up the Box MCP (Model Context Protocol) server for use with Cursor AI.

## ✅ Completed Steps

1. ✅ **Repository Cloned**: The Box MCP server repository has been cloned to `mcp-server-box/`
2. ✅ **Dependencies Installed**: All Python dependencies have been installed using `uv`
3. ✅ **Configuration Files Created**: Environment template and Cursor MCP configuration are ready

## 🔧 Next Steps - Configuration Required

### Step 1: Get Box Developer Credentials

1. Go to [Box Developer Console](https://app.box.com/developers/console)
2. Sign in with your Box account
3. Click **"Create New App"**
4. Choose **"Custom App"** → **"User Authentication (OAuth 2.0)"**
5. Configure your app:
   - **App Name**: Give it a name (e.g., "Cursor MCP Server")
   - **Redirect URI**: Add `http://localhost:8000/callback`
6. After creating, you'll see:
   - **Client ID** - Copy this
   - **Client Secret** - Copy this (click "Reveal" to see it)

### Step 2: Configure Environment Variables

1. Navigate to the `mcp-server-box` directory:
   ```bash
   cd /Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box
   ```

2. Create a `.env` file (copy from the example):
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your Box credentials:
   ```bash
   # Open in your preferred editor
   nano .env
   # or
   code .env
   ```

4. Update the following values:
   ```ini
   BOX_CLIENT_ID=your_actual_client_id_here
   BOX_CLIENT_SECRET=your_actual_client_secret_here
   BOX_REDIRECT_URL=http://localhost:8000/callback
   
   # Optional: Generate a secure token
   BOX_MCP_SERVER_AUTH_TOKEN=
   
   LOG_LEVEL=INFO
   ```

5. **Generate a secure token** (optional, for additional security):
   ```bash
   openssl rand -base64 32
   ```
   Copy the output and paste it as the value for `BOX_MCP_SERVER_AUTH_TOKEN`

### Step 3: Verify Cursor MCP Configuration

The MCP server has already been configured in Cursor at:
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

The configuration should look like:
```json
{
  "mcpServers": {
    "box": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box",
        "run",
        "src/mcp_server_box.py"
      ]
    }
  }
}
```

### Step 4: Test the Setup

1. **Restart Cursor** completely (quit and reopen)

2. **Test the MCP server** by running it manually first:
   ```bash
   cd /Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box
   uv run src/mcp_server_box.py
   ```
   
   You should see the server start. Press `Ctrl+C` to stop it.

3. **In Cursor**, try using Box-related commands in the AI chat:
   - "List my Box files"
   - "Search for documents in my Box account"
   - "What files do I have in Box?"

4. **First-time authentication**: When you first use Box features, you'll be prompted to authorize the app in your browser. Follow the OAuth flow to grant permissions.

## 🔍 Troubleshooting

### Server Won't Start
- **Check Python version**: `python3 --version` (should be 3.8+)
- **Verify dependencies**: `cd mcp-server-box && uv sync`
- **Check .env file**: Ensure all required variables are set

### Authentication Errors
- **Verify credentials**: Double-check `BOX_CLIENT_ID` and `BOX_CLIENT_SECRET` in `.env`
- **Check redirect URL**: Must match what's configured in Box Developer Console
- **Re-authorize**: You may need to re-authenticate if tokens expire

### Cursor Not Recognizing MCP Server
- **Restart Cursor**: Fully quit and reopen the application
- **Check configuration**: Verify `cline_mcp_settings.json` has the correct path
- **Check logs**: Look for MCP-related errors in Cursor's output panel

### Permission Errors
- **Box App Authorization**: Ensure your Box app is authorized by your Box admin (if required)
- **OAuth Scopes**: Check that your Box app has the necessary scopes/permissions

## 📚 Additional Resources

- [Box Developer Documentation](https://developer.box.com/)
- [Box MCP Server Repository](https://github.com/box-community/mcp-server-box)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Authentication Guide](mcp-server-box/docs/authentication.md)

## 🎯 What You Can Do With Box MCP Server

Once set up, you can use Cursor AI to:
- **Search** files and folders in your Box account
- **Read** and analyze Box documents
- **Upload** files to Box
- **Manage** folders and files
- **Generate** documents using Box AI features
- **Collaborate** on files with team members
- And much more!

## 🔐 Security Notes

- **Never commit `.env` file**: It contains sensitive credentials
- **Keep tokens secure**: Don't share your `BOX_MCP_SERVER_AUTH_TOKEN`
- **Rotate credentials**: Regularly update your Box app credentials
- **Use appropriate scopes**: Only grant necessary permissions in your Box app

---

**Need Help?** Check the [Box MCP Server Documentation](mcp-server-box/README.md) or the [Authentication Guide](mcp-server-box/docs/authentication.md) for more details.

