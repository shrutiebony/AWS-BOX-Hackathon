#!/usr/bin/env python3
"""
AWS Bedrock Service
Handles AI analysis using AWS Bedrock instead of Box AI.
"""

import json
import logging
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BedrockService:
    """Service for interacting with AWS Bedrock."""
    
    def __init__(self, region_name: Optional[str] = None, model_id: Optional[str] = None):
        """
        Initialize Bedrock service.
        
        Args:
            region_name: AWS region (defaults to AWS_DEFAULT_REGION or us-east-1)
            model_id: Bedrock model ID (defaults to anthropic.claude-3-sonnet-20240229-v1:0)
        """
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        # Default to Claude 3 Sonnet, but allow override via environment variable
        self.model_id = model_id or os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        
        try:
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                region_name=self.region_name
            )
            logger.info(f"✅ Bedrock service initialized (Region: {self.region_name}, Model: {self.model_id})")
        except Exception as e:
            logger.error(f"❌ Error initializing Bedrock client: {e}")
            raise
    
    def invoke_model(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """
        Invoke Bedrock model with a prompt.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response (default: 4096)
            temperature: Temperature for generation (default: 0.7)
            
        Returns:
            The model's response text
        """
        try:
            # Prepare the request body for Claude models
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse the response
            response_body_str = response['body'].read()
            if isinstance(response_body_str, bytes):
                response_body_str = response_body_str.decode('utf-8')
            response_body = json.loads(response_body_str)
            
            # Extract the text from Claude's response
            if 'content' in response_body:
                # Claude returns content as a list of content blocks
                content_blocks = response_body['content']
                if isinstance(content_blocks, list) and len(content_blocks) > 0:
                    # Get the text from the first content block
                    text = content_blocks[0].get('text', '')
                    return text
                elif isinstance(content_blocks, str):
                    return content_blocks
            elif 'text' in response_body:
                return response_body['text']
            else:
                # Fallback: return the whole response as string
                logger.warning(f"Unexpected response format: {response_body}")
                return str(response_body)
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Bedrock API error ({error_code}): {error_message}")
            raise ValueError(f"Bedrock API error: {error_message}")
        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            raise
    
    async def analyze_contract(
        self,
        contract_text: str,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.7
    ) -> str:
        """
        Analyze a contract using Bedrock.
        
        Args:
            contract_text: The contract text to analyze
            prompt: The analysis prompt/instructions
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            
        Returns:
            The analysis result
        """
        # Combine contract text and prompt
        full_prompt = f"""{prompt}

CONTRACT TEXT:
{contract_text}

Please analyze the contract above and provide your response."""
        
        return self.invoke_model(full_prompt, max_tokens=max_tokens, temperature=temperature)
    
    async def generate_content(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        Generate content using Bedrock.
        
        Args:
            prompt: The prompt for content generation
            max_tokens: Maximum tokens in response
            
        Returns:
            The generated content
        """
        return self.invoke_model(prompt, max_tokens=max_tokens)

