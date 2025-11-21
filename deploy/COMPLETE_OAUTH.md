# Complete Box OAuth Authorization

## Quick Steps

1. **Get the Authorization URL:**
   ```bash
   ssh -i deploy/contract-protection-key.pem ec2-user@3.239.89.25 \
       "cd /opt/contract-protection-system/mcp-server-box && \
        source ~/.cargo/env && \
        uv run python3 /tmp/get_oauth_url.py"
   ```

2. **Open the URL in your browser** and authorize the application

3. **Copy the authorization code** from the redirect URL (the `code=` parameter)

4. **Complete OAuth:**
   ```bash
   ssh -i deploy/contract-protection-key.pem ec2-user@3.239.89.25 \
       "cd /opt/contract-protection-system/mcp-server-box && \
        source ~/.cargo/env && \
        uv run python3 /tmp/complete_oauth.py YOUR_AUTHORIZATION_CODE"
   ```

5. **Verify:**
   ```bash
   ssh -i deploy/contract-protection-key.pem ec2-user@3.239.89.25 \
       "sudo systemctl status contract-protection-system"
   ```

## Automated Script

Or run this all-in-one script:

```bash
./complete-oauth-flow.sh
```

