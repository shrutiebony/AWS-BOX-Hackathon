#!/usr/bin/env python3
"""
Box Contract Service
Handles all Box API interactions for the contract protection system.
Uses the same authentication system as the MCP server.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add mcp-server-box src to path
mcp_server_path = Path(__file__).parent / "mcp-server-box" / "src"
sys.path.insert(0, str(mcp_server_path))

from box_ai_agents_toolkit import (
    box_file_text_extract,
    box_folder_create,
    box_folder_items_list,
    box_file_upload,
    box_ai_ask_file_single,
)
from box_sdk_gen import BoxClient, BoxSDKError
from config import AppConfig
from dotenv import load_dotenv
from mcp_auth.auth_box_api import get_oauth_client, get_oauth_config
from box_sdk_gen import BoxOAuth, BoxClient, FileWithInMemoryCacheTokenStorage

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BoxContractService:
    """Service for interacting with Box API."""
    
    def __init__(self):
        self.client: Optional[BoxClient] = None
        
    async def initialize(self):
        """Initialize Box client with OAuth."""
        # Load configuration from environment
        app_config = AppConfig.from_env()
        box_config = app_config.box_api
        
        if not box_config.client_id or not box_config.client_secret:
            raise ValueError("BOX_CLIENT_ID and BOX_CLIENT_SECRET must be set in .env")
        
        # Create OAuth client
        logger.info("Initializing Box OAuth client...")
        try:
            # Use token file from mcp-server-box directory if it exists
            token_file = Path(__file__).parent / "mcp-server-box" / ".auth.oauth"
            if not token_file.exists():
                token_file = Path(__file__).parent / ".auth.oauth"
            
            # Create OAuth config with correct token storage path
            oauth_config = get_oauth_config(box_config)
            # Override token storage to use absolute path
            oauth_config.token_storage = FileWithInMemoryCacheTokenStorage(str(token_file))
            
            auth = BoxOAuth(oauth_config)
            self.client = BoxClient(auth=auth)
            logger.info("Box service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Box client: {e}")
            logger.info("You may need to complete OAuth authorization first.")
            logger.info("Try running the MCP server to complete OAuth flow.")
            raise
    
    def _get_client(self) -> BoxClient:
        """Get authenticated Box client."""
        if not self.client:
            raise RuntimeError("Box client not initialized. Call initialize() first.")
        return self.client
    
    async def find_or_create_folder(
        self, parent_folder_id: str, folder_name: str
    ) -> str:
        """Find folder by name or create it if it doesn't exist."""
        if not parent_folder_id or parent_folder_id == "None":
            raise ValueError(f"Invalid parent_folder_id: {parent_folder_id}. Cannot find or create folder '{folder_name}'.")
        
        client = self._get_client()
        
        try:
            # First, try to list items and find existing folder
            try:
                items = await self.list_folder_items(parent_folder_id)
                
                # Look for existing folder
                for item in items:
                    if item['type'] == 'folder' and item['name'] == folder_name:
                        logger.info(f"Found existing folder: {folder_name} (ID: {item['id']})")
                        return item['id']
            except Exception as list_error:
                logger.warning(f"Could not list folder items: {list_error}, will try to create")
            
            # Create new folder if not found
            logger.info(f"Creating new folder: {folder_name}")
            try:
                result = box_folder_create(
                    client=client,
                    name=folder_name,
                    parent_folder_id=parent_folder_id
                )
                
                # Check if result is an error response (some functions return error dict instead of raising)
                if isinstance(result, dict) and 'error' in result:
                    error_msg = result.get('error', '')
                    if '409' in error_msg or 'already exists' in error_msg.lower():
                        logger.info(f"Folder {folder_name} already exists (from error dict), finding it...")
                        # The folder exists, use client.folders directly to find it
                        try:
                            # Use client's folders manager
                            items = client.folders.get_folder_items(parent_folder_id)
                            for item in items.entries:
                                if item.type == 'folder' and item.name == folder_name:
                                    logger.info(f"✅ Found existing folder via SDK: {item.id}")
                                    return item.id
                            # If not found, raise error
                            raise ValueError(f"Folder {folder_name} exists but not found in parent folder listing")
                        except Exception as sdk_err:
                            logger.error(f"Could not find folder via SDK: {sdk_err}")
                            raise ValueError(f"Folder {folder_name} exists but could not retrieve its ID: {sdk_err}")
                    else:
                        raise ValueError(f"Error creating folder: {error_msg}")
                
                # Extract folder ID from successful creation
                # Result can be in different formats: {'id': '...'}, {'folder': {'id': '...'}}, or {'folder_id': '...'}
                if isinstance(result, dict):
                    folder_id = result.get('id', '')
                    if not folder_id:
                        # Check if nested under 'folder' key
                        folder_id = result.get('folder', {}).get('id', '')
                    if not folder_id:
                        folder_id = result.get('folder_id', '')
                    if not folder_id:
                        # Check nested 'item' structure
                        folder_id = result.get('item', {}).get('id', '')
                else:
                    folder_id = str(result) if result else ''
                
                if folder_id:
                    logger.info(f"✅ Created folder: {folder_name} (ID: {folder_id})")
                    return folder_id
                else:
                    raise ValueError(f"Could not extract folder ID from result: {result}")
                    
            except BoxSDKError as e:
                # If folder already exists (409), extract ID from error and use existing folder
                if e.status == 409:
                    logger.info(f"Folder {folder_name} already exists (409), using existing folder...")
                    # Extract folder ID from error context_info - this is the most reliable way
                    folder_id = None
                    try:
                        # The error has context_info with conflicts containing the folder ID
                        if hasattr(e, 'context_info') and e.context_info:
                            conflicts = getattr(e.context_info, 'conflicts', [])
                            if conflicts:
                                conflict = conflicts[0] if isinstance(conflicts, list) else conflicts
                                folder_id = conflict.get('id') if isinstance(conflict, dict) else getattr(conflict, 'id', None)
                                if folder_id:
                                    logger.info(f"✅ Using existing folder ID from error: {folder_id}")
                                    return str(folder_id)
                    except Exception as parse_err:
                        logger.debug(f"Could not parse context_info: {parse_err}")
                    
                    # Fallback: try to find by listing (this should work)
                    if not folder_id:
                        try:
                            logger.info(f"Searching for folder {folder_name} by listing parent folder...")
                            items = await self.list_folder_items(parent_folder_id)
                            for item in items:
                                if item['type'] == 'folder' and item['name'] == folder_name:
                                    folder_id = item['id']
                                    logger.info(f"✅ Found existing folder by listing: {folder_id}")
                                    return folder_id
                        except Exception as list_err:
                            logger.error(f"Could not list items to find folder: {list_err}")
                            raise ValueError(f"Folder {folder_name} exists but could not retrieve its ID. Error: {list_err}")
                    
                    # If we still don't have the ID, that's a problem
                    if not folder_id:
                        raise ValueError(f"Folder {folder_name} exists but could not retrieve its ID from error or listing")
                else:
                    # Not a 409 error, re-raise it
                    raise
                    
            except Exception as e:
                # For any other exception, check if it's a 409
                error_str = str(e)
                if '409' in error_str or 'already exists' in error_str.lower() or 'item_name_in_use' in error_str:
                    logger.info(f"Folder {folder_name} already exists (generic exception), searching...")
                    try:
                        items = await self.list_folder_items(parent_folder_id)
                        for item in items:
                            if item['type'] == 'folder' and item['name'] == folder_name:
                                logger.info(f"Found existing folder: {item['id']}")
                                return item['id']
                    except:
                        pass
                raise
                
        except Exception as e:
            logger.error(f"Error finding/creating folder {folder_name}: {e}")
            raise
    
    async def find_file_in_folder(
        self, folder_id: str, filename: str
    ) -> Optional[str]:
        """Find a file by name in a folder. Returns file ID or None."""
        client = self._get_client()
        
        try:
            # Use client.folders directly
            items = client.folders.get_folder_items(folder_id)
            
            for item in items.entries:
                if item.type == "file" and item.name == filename:
                    return item.id
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding file {filename}: {e}")
            return None
    
    async def list_folder_items(self, folder_id: str) -> List[Dict]:
        """List all items in a folder."""
        if not folder_id or folder_id == "None":
            raise ValueError(f"Invalid folder_id: {folder_id}. Cannot list folder items.")
        
        client = self._get_client()
        
        try:
            # Use SDK directly for reliable results
            items_response = client.folders.get_folder_items(folder_id)
            
            # Convert to list of dicts
            items = []
            for item in items_response.entries:
                # Determine type: 'file' or 'folder'
                item_type = 'file' if str(item.type) == 'FileBaseTypeField.FILE' else 'folder'
                
                items.append({
                    'id': item.id,
                    'name': item.name,
                    'type': item_type,
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Error listing folder items: {e}")
            raise
    
    async def read_file(self, file_id: str) -> str:
        """Read text content from a Box file."""
        client = self._get_client()
        
        try:
            # Use Box text extraction
            result = box_file_text_extract(client, file_id)
            
            # Extract text from result
            if isinstance(result, dict):
                text = result.get('text', result.get('content', str(result)))
            else:
                text = str(result)
            
            return text
            
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {e}")
            raise
    
    async def upload_text_file(
        self, folder_id: str, filename: str, content: str
    ) -> str:
        """Upload a text file to Box."""
        client = self._get_client()
        
        try:
            # Convert string to bytes
            file_bytes = content.encode('utf-8')
            
            # Upload file using Box AI toolkit
            result = box_file_upload(
                client=client,
                content=file_bytes,
                file_name=filename,
                parent_folder_id=folder_id
            )
            
            # Extract file ID from result
            if isinstance(result, dict):
                file_id = result.get('id', result.get('file_id', ''))
            else:
                file_id = str(result)
            
            logger.info(f"Uploaded file: {filename}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise
    
    async def upload_document_file(
        self, folder_id: str, filename: str, content: str, file_type: str = "docx"
    ) -> str:
        """
        Upload a formatted document file (DOCX or PDF) to Box.
        
        Args:
            folder_id: Box folder ID
            filename: Name of the file (should have .docx or .pdf extension)
            content: Text content to convert to document
            file_type: Type of document ("docx" or "pdf")
            
        Returns:
            File ID of uploaded document
        """
        from document_generator import create_docx_from_text, create_pdf_from_text
        
        client = self._get_client()
        
        try:
            # Generate proper document format
            if filename.endswith('.docx') or file_type.lower() == 'docx':
                file_bytes = create_docx_from_text(content, title=None)
            elif filename.endswith('.pdf') or file_type.lower() == 'pdf':
                file_bytes = create_pdf_from_text(content, title=None)
            else:
                # Fallback to plain text
                logger.warning(f"Unknown file type for {filename}, using plain text")
                file_bytes = content.encode('utf-8')
            
            # Upload file using Box AI toolkit
            result = box_file_upload(
                client=client,
                content=file_bytes,
                file_name=filename,
                parent_folder_id=folder_id
            )
            
            # Extract file ID from result
            if isinstance(result, dict):
                file_id = result.get('id', result.get('file_id', ''))
            else:
                file_id = str(result)
            
            logger.info(f"Uploaded formatted document: {filename}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error uploading document {filename}: {e}")
            raise
    
    async def ask_ai_about_file(self, file_id: str, prompt: str) -> str:
        """
        Use AWS Bedrock to analyze a file.
        Reads the file from Box and sends it to Bedrock for analysis.
        """
        try:
            # Read the file content from Box first
            contract_text = await self.read_file(file_id)
            
            # Import BedrockService here to avoid circular imports
            from bedrock_service import BedrockService
            
            # Initialize Bedrock service
            bedrock = BedrockService()
            
            # Use Bedrock to analyze the contract
            logger.info(f"Using AWS Bedrock to analyze file {file_id}")
            result = await bedrock.analyze_contract(
                contract_text=contract_text,
                prompt=prompt,
                max_tokens=8192,
                temperature=0.7
            )
            
            if not result or len(result.strip()) < 10:
                logger.warning(f"Bedrock returned very short or empty response")
                raise ValueError("Bedrock returned empty or invalid response")
            
            return result
            
        except ImportError:
            logger.error("BedrockService not found. Please ensure bedrock_service.py exists.")
            raise
        except Exception as e:
            logger.error(f"Error calling Bedrock: {e}")
            raise
    
    async def get_current_user_email(self) -> Optional[str]:
        """Get the current authenticated user's email from Box."""
        client = self._get_client()
        
        try:
            # Get current user info
            current_user = client.users.get_user_me()
            user_dict = current_user.to_dict()
            
            # Extract email from login field (Box uses 'login' for email)
            email = user_dict.get('login') or user_dict.get('email')
            
            if email:
                logger.info(f"Retrieved user email from Box: {email}")
                return email
            else:
                logger.warning("Could not find email in user info")
                logger.debug(f"User info keys: {list(user_dict.keys())}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user email from Box: {e}")
            return None

