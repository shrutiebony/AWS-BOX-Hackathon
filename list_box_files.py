#!/usr/bin/env python3
"""
Simple script to list Box files using the Box SDK.
This script uses OAuth 2.0 authentication.
"""

import os
import sys
from pathlib import Path

# Add the mcp-server-box directory to the path
mcp_server_path = Path(__file__).parent / "mcp-server-box"
sys.path.insert(0, str(mcp_server_path / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(mcp_server_path / ".env")

try:
    from box_sdk_gen import (
        BoxClient,
        BoxDeveloperTokenAuth,
        BoxOAuth,
        OAuthConfig,
        FileWithInMemoryCacheTokenStorage,
        GetAuthorizeUrlOptions,
    )
except ImportError:
    print("Error: Box SDK not found. Make sure dependencies are installed.")
    print("Run: cd mcp-server-box && uv sync")
    sys.exit(1)

def authenticate_box():
    """Authenticate with Box using OAuth 2.0"""
    client_id = os.getenv("BOX_CLIENT_ID")
    client_secret = os.getenv("BOX_CLIENT_SECRET")
    redirect_url = os.getenv("BOX_REDIRECT_URL", "http://localhost:8000/callback")
    
    if not client_id or not client_secret:
        print("Error: BOX_CLIENT_ID and BOX_CLIENT_SECRET must be set in .env file")
        sys.exit(1)
    
    # Create OAuth config
    oauth_config = OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        token_storage=FileWithInMemoryCacheTokenStorage(".auth.oauth"),
    )
    
    oauth = BoxOAuth(oauth_config)
    
    # Get authorization URL
    auth_url_options = GetAuthorizeUrlOptions(redirect_uri=redirect_url)
    auth_url = oauth.get_authorize_url(options=auth_url_options)
    print(f"\n🔐 Please authorize the app:")
    print(f"1. Open this URL in your browser: {auth_url}")
    print("2. Authorize the application")
    print("3. Copy the authorization code from the redirect URL")
    
    auth_code = input("\nEnter the authorization code: ").strip()
    
    try:
        access_token_obj = oauth.get_tokens_authorization_code_grant(auth_code)
        access_token = access_token_obj.access_token
        refresh_token = access_token_obj.refresh_token if hasattr(access_token_obj, 'refresh_token') else None
        return access_token, refresh_token
    except Exception as e:
        print(f"Error during authentication: {e}")
        sys.exit(1)

def list_files(access_token: str, folder_id: str = "0", recursive: bool = False):
    """List files in a Box folder"""
    auth = BoxDeveloperTokenAuth(token=access_token)
    client = BoxClient(auth=auth)
    
    try:
        if folder_id == "0":
            folder = client.folders.get_folder_by_id("0")
        else:
            folder = client.folders.get_folder_by_id(folder_id)
        
        print(f"\n📁 Folder: {folder.name} (ID: {folder.id})")
        print("=" * 60)
        
        items = client.folders.get_folder_items(folder_id, limit=100)
        
        if not items.entries:
            print("(Empty folder)")
            return
        
        files = []
        folders = []
        
        for item in items.entries:
            if item.type == "file":
                files.append(item)
            elif item.type == "folder":
                folders.append(item)
        
        if folders:
            print("\n📂 Folders:")
            for folder in folders:
                print(f"  • {folder.name} (ID: {folder.id})")
        
        if files:
            print("\n📄 Files:")
            for file in files:
                size_mb = file.size / (1024 * 1024) if file.size else 0
                print(f"  • {file.name} ({size_mb:.2f} MB) (ID: {file.id})")
        
        print(f"\nTotal: {len(folders)} folders, {len(files)} files")
        
        if recursive and folders:
            print("\n" + "=" * 60)
            for folder in folders:
                print(f"\n📂 Subfolder: {folder.name}")
                list_files(access_token, folder.id, recursive=True)
        
    except Exception as e:
        print(f"Error listing files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Box File Lister")
    print("=" * 60)
    
    # Authenticate
    access_token, refresh_token = authenticate_box()
    
    # List files in root folder
    list_files(access_token, folder_id="0", recursive=False)
    
    print("\n✅ Done!")

