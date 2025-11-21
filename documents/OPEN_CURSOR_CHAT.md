# How to Open Cursor's Chat and Use Box MCP

## 🚀 Quick Steps to Open Cursor Chat

### Method 1: Keyboard Shortcut (Fastest)
1. **Press `Cmd+L`** (macOS) - This opens Cursor's chat/composer
2. Type: `List my Box files`
3. Press Enter

### Method 2: Command Palette
1. **Press `Cmd+Shift+P`** to open Command Palette
2. Type: `Chat` or `Composer`
3. Select the chat/composer option
4. Type: `List my Box files`

### Method 3: UI Button
1. Look for the **chat/composer icon** in Cursor's sidebar (usually at the top)
2. Click it to open the chat
3. Type: `List my Box files`

### Method 4: Inline Chat
1. **Select some code or text** in your editor
2. **Press `Cmd+K`** - This opens inline chat
3. Type: `List my Box files`

## 📝 What to Type in Chat

Once the chat is open, try these commands:

- `List my Box files`
- `Show me what's in my Box account`
- `What files do I have in Box?`
- `Search for documents in my Box account`
- `List folders in my Box root directory`

## 🔐 First-Time Authentication

When you first use Box features:
1. Cursor will automatically open your browser
2. You'll see the Box authorization page
3. Click **"Authorize"** or **"Grant Access"**
4. You'll be redirected back to Cursor
5. The chat should now show your Box files

## ✅ Verify Setup Before Using

Your Box MCP server is configured at:
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

Your Box credentials are in:
```
/Users/sameer/Documents/hackathon/AWS-BOX/mcp-server-box/.env
```

## 🆘 If It Doesn't Work

1. **Restart Cursor** completely (Cmd+Q, then reopen)
2. **Check for errors** in Cursor's output panel (View → Output)
3. **Verify credentials** are correct in the `.env` file
4. **Check Box app** has redirect URI `http://localhost:8000/callback` configured

---

**Ready?** Press `Cmd+L` and type "List my Box files"! 🎯

