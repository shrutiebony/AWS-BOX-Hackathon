#!/usr/bin/env python3
"""
Contract Protection System
Monitors Box contracts folder and generates protected mirror contracts.
"""

import asyncio
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from box_contract_service import BoxContractService
from action_item_detector import ActionItemDetector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContractProcessor:
    """Processes contracts and generates protected versions."""
    
    # Box folder names
    CONTRACTS_FOLDER = "Smart_Contracts"
    PROTECT_INTERESTS_FOLDER = "protect_your_interests"
    MY_INTERESTS_FOLDER = "my_interests"
    MY_INTERESTS_FILE = "MY_INTERESTS.txt"
    
    # Contract categories
    CONTRACT_CATEGORIES = [
        "Service Contract",
        "Employment Contract",
        "Lease and Rent Agreement",
        "Non-Disclosure Agreement (NDA)",
        "Partnership and Joint Venture Agreement",
        "Loan and Financing Contract",
        "Government and Procurement Contract",
        "Software License Agreement",
        "Freelancer and Contractor Agreement"
    ]
    
    def __init__(self):
        self.box_service = BoxContractService()
        self.processed_contracts = set()  # Track processed contracts
        self.category_folder_ids = {}  # Store category folder IDs
        self.action_detector = ActionItemDetector(box_service=self.box_service)  # Action item detector
        self.checked_contracts = set()  # Track contracts checked for action items
        
    async def initialize(self):
        """Initialize Box service and create necessary folders."""
        await self.box_service.initialize()
        await self._ensure_folders_exist()
        
    async def _ensure_folders_exist(self):
        """Ensure required folders exist in Box."""
        root_id = "0"
        
        # Create contracts folder if it doesn't exist
        contracts_folder_id = await self.box_service.find_or_create_folder(
            root_id, self.CONTRACTS_FOLDER
        )
        logger.info(f"Contracts folder ID: {contracts_folder_id}")
        
        # Create protect_your_interests folder
        protect_folder_id = await self.box_service.find_or_create_folder(
            root_id, self.PROTECT_INTERESTS_FOLDER
        )
        logger.info(f"Protect interests folder ID: {protect_folder_id}")
        
        # Create category subfolders inside protect_your_interests
        self.category_folder_ids = {}
        for category in self.CONTRACT_CATEGORIES:
            category_folder_id = await self.box_service.find_or_create_folder(
                protect_folder_id, category
            )
            self.category_folder_ids[category] = category_folder_id
            logger.info(f"Created category folder: {category} (ID: {category_folder_id})")
        
        # Create my_interests folder
        interests_folder_id = await self.box_service.find_or_create_folder(
            root_id, self.MY_INTERESTS_FOLDER
        )
        logger.info(f"Interests folder ID: {interests_folder_id}")
        
        # Store folder IDs
        self.contracts_folder_id = contracts_folder_id
        self.protect_folder_id = protect_folder_id
        self.interests_folder_id = interests_folder_id
        
    async def get_user_interests(self) -> Optional[str]:
        """Load user interests from Box. Returns None if not found."""
        try:
            # Find MY_INTERESTS.txt in my_interests folder
            interests_file_id = await self.box_service.find_file_in_folder(
                self.interests_folder_id, self.MY_INTERESTS_FILE
            )
            
            if interests_file_id:
                interests_text = await self.box_service.read_file(interests_file_id)
                logger.info("Loaded user interests from Box")
                return interests_text
            else:
                logger.info(f"{self.MY_INTERESTS_FILE} not found. Will make contract fairer without user interests.")
                return None
                
        except Exception as e:
            logger.error(f"Error loading user interests: {e}")
            return None
    
    async def get_per_contract_instructions(self, contract_name: str) -> Optional[str]:
        """Get per-contract instructions if they exist."""
        try:
            # Look for {contract_name}.instructions file
            instructions_filename = f"{contract_name}.instructions"
            instructions_file_id = await self.box_service.find_file_in_folder(
                self.contracts_folder_id, instructions_filename
            )
            
            if instructions_file_id:
                instructions = await self.box_service.read_file(instructions_file_id)
                logger.info(f"Found per-contract instructions for {contract_name}")
                return instructions
            return None
            
        except Exception as e:
            logger.error(f"Error loading per-contract instructions: {e}")
            return None
    
    async def classify_contract(
        self,
        contract_file_id: str,
        contract_text: str
    ) -> str:
        """Classify contract into one of the predefined categories using Box AI."""
        
        categories_list = "\n".join([f"- {cat}" for cat in self.CONTRACT_CATEGORIES])
        
        classification_prompt = f"""Analyze this contract and classify it into ONE of the following categories:

{categories_list}

Contract content (first 3000 characters):
{contract_text[:3000]}...

IMPORTANT: 
- Respond with ONLY the exact category name from the list above
- Choose the most appropriate category
- If it doesn't fit any category, choose the closest match
- Do not include any explanation, just the category name

Category:"""
        
        try:
            classification = await self.box_service.ask_ai_about_file(
                contract_file_id, classification_prompt
            )
            
            # Clean up the response - extract just the category name
            classification = classification.strip()
            
            # Remove any quotes or extra text
            classification = classification.strip('"').strip("'").strip()
            
            # Check if it's a valid category (exact match or contains category name)
            for category in self.CONTRACT_CATEGORIES:
                if category.lower() == classification.lower():
                    logger.info(f"Contract classified as: {category}")
                    return category
                # Also check if category name is contained in response
                if category.lower() in classification.lower() or classification.lower() in category.lower():
                    logger.info(f"Contract classified as: {category} (fuzzy match)")
                    return category
            
            # If no exact match, try to find closest
            # Default to first category if can't determine
            logger.warning(f"Could not determine category from: {classification}. Using default: {self.CONTRACT_CATEGORIES[0]}")
            return self.CONTRACT_CATEGORIES[0]
            
        except Exception as e:
            logger.error(f"Error classifying contract: {e}")
            # Default to first category on error
            logger.warning(f"Using default category: {self.CONTRACT_CATEGORIES[0]}")
            return self.CONTRACT_CATEGORIES[0]
    
    def _extract_contract_name(self, filename: str) -> str:
        """Extract contract name from filename (remove extension)."""
        # Remove file extension
        name = Path(filename).stem
        # Remove .instructions if present
        if name.endswith('.instructions'):
            name = name[:-13]
        return name
    
    def _is_contract_file(self, filename: str) -> bool:
        """Check if file is a contract (not instructions or other files)."""
        # Skip instruction files
        if filename.endswith('.instructions'):
            return False
        # Skip system files
        if filename.startswith('.'):
            return False
        # Common contract file extensions
        contract_extensions = ['.pdf', '.doc', '.docx', '.txt']
        return any(filename.lower().endswith(ext) for ext in contract_extensions)
    
    async def process_new_contracts(self):
        """Check for new contracts and process them."""
        try:
            # List all files in contracts folder
            items = await self.box_service.list_folder_items(self.contracts_folder_id)
            
            contracts_to_process = []
            
            for item in items:
                if item['type'] == 'file':
                    filename = item['name']
                    file_id = item['id']
                    
                    # Check if it's a contract file
                    if self._is_contract_file(filename):
                        contract_name = self._extract_contract_name(filename)
                        contract_key = f"{contract_name}_{file_id}"
                        
                        # Check if we've already processed this contract
                        if contract_key not in self.processed_contracts:
                            contracts_to_process.append({
                                'file_id': file_id,
                                'filename': filename,
                                'contract_name': contract_name
                            })
            
            # Process each new contract
            for contract in contracts_to_process:
                contract_key = f"{contract['contract_name']}_{contract['file_id']}"
                try:
                    await self.process_contract(
                        contract['file_id'],
                        contract['filename'],
                        contract['contract_name']
                    )
                    # Mark as processed only on success
                    self.processed_contracts.add(contract_key)
                    logger.info(f"✅ Marked {contract['filename']} as processed")
                except Exception as e:
                    logger.error(f"❌ Failed to process {contract['filename']}: {e}")
                    # Mark as processed even on failure to prevent infinite retries
                    # (You can remove this line if you want to retry failed contracts)
                    self.processed_contracts.add(contract_key)
                    logger.warning(f"⚠️  Marked {contract['filename']} as processed (failed) to prevent retry loop")
                
        except Exception as e:
            logger.error(f"Error checking for new contracts: {e}")
    
    async def check_all_contracts_for_action_items(self):
        """Check all contracts in contracts folder for action items."""
        try:
            logger.info("Checking all contracts for action items...")
            
            # Get user email from Box if not set
            if not self.action_detector.user_email:
                email = await self.action_detector.get_user_email_from_box()
                if email:
                    logger.info(f"Using email from Box: {email}")
                    # Also set SNS topic ARN if not set
                    if not self.action_detector.sns_topic_arn:
                        self.action_detector.sns_topic_arn = os.getenv(
                            "AWS_SNS_TOPIC_ARN",
                            "arn:aws:sns:us-east-1:440588070262:contract-action-items"
                        )
            
            # List all files in contracts folder
            items = await self.box_service.list_folder_items(self.contracts_folder_id)
            
            all_action_items = []
            
            for item in items:
                if item['type'] == 'file':
                    filename = item['name']
                    file_id = item['id']
                    
                    # Check if it's a contract file
                    if self._is_contract_file(filename):
                        try:
                            # Read contract content
                            contract_text = await self.box_service.read_file(file_id)
                            
                            # Analyze for action items
                            action_items = await self.action_detector.analyze_contract_for_action_items(
                                self.box_service,
                                file_id,
                                filename,
                                contract_text
                            )
                            
                            if action_items:
                                logger.info(f"Found {len(action_items)} action item(s) in {filename}")
                                all_action_items.extend(action_items)
                            else:
                                logger.debug(f"No action items found in {filename}")
                                
                        except Exception as e:
                            logger.error(f"Error checking action items for {filename}: {e}")
                            continue
            
            # Filter for urgent items
            urgent_items = self.action_detector.filter_urgent_action_items(all_action_items)
            
            if urgent_items:
                logger.info(f"Found {len(urgent_items)} urgent action item(s)")
                # Send notification
                self.action_detector.send_notification(urgent_items)
            else:
                logger.info("No urgent action items found")
            
            return urgent_items
            
        except Exception as e:
            logger.error(f"Error checking contracts for action items: {e}")
            return []
    
    async def process_contract(
        self,
        contract_file_id: str,
        contract_filename: str,
        contract_name: str
    ):
        """Process a single contract and generate protected version."""
        logger.info(f"Processing contract: {contract_filename}")
        
        try:
            # Read contract content
            contract_text = await self.box_service.read_file(contract_file_id)
            
            # Classify the contract
            contract_category = await self.classify_contract(
                contract_file_id, contract_text
            )
            logger.info(f"Contract classified as: {contract_category}")
            
            # Get user interests
            user_interests = await self.get_user_interests()
            
            # Get per-contract instructions if they exist
            per_contract_instructions = await self.get_per_contract_instructions(
                contract_name
            )
            
            # Get the category folder ID
            category_folder_id = self.category_folder_ids.get(contract_category)
            if not category_folder_id:
                logger.warning(f"Category folder not found for {contract_category}, using default")
                category_folder_id = list(self.category_folder_ids.values())[0]
            
            # Create mirror folder inside the category folder
            mirror_folder_name = f"{contract_name}_mirror"
            mirror_folder_id = await self.box_service.find_or_create_folder(
                category_folder_id, mirror_folder_name
            )
            
            # Generate the 3 output files using Box AI
            await self._generate_protected_contract(
                contract_file_id,
                contract_text,
                user_interests,
                per_contract_instructions,
                mirror_folder_id,
                contract_name,
                contract_category
            )
            
            logger.info(f"✅ Successfully processed: {contract_filename} → {contract_category}")
            
        except Exception as e:
            logger.error(f"Error processing contract {contract_filename}: {e}")
            raise
    
    async def _generate_protected_contract(
        self,
        contract_file_id: str,
        contract_text: str,
        user_interests: Optional[str],
        per_contract_instructions: Optional[str],
        mirror_folder_id: str,
        contract_name: str,
        contract_category: str
    ):
        """Use Box AI to generate the 3 protected contract files."""
        
        # Build the prompt for Box AI
        prompt = self._build_analysis_prompt(
            contract_text,
            user_interests,
            per_contract_instructions,
            contract_category
        )
        
        # Use AWS Bedrock to analyze and generate
        logger.info("Calling AWS Bedrock to analyze contract...")
        
        # File 1: Mirror contract
        mirror_prompt = f"""{prompt}

Generate the complete rewritten contract (File 1) that protects the user's interests while keeping non-negotiables intact. 
Output the full contract text in a clear, professional format suitable for a .docx file."""
        
        try:
            mirror_contract = await self.box_service.ask_ai_about_file(
                contract_file_id, mirror_prompt
            )
        except Exception as e:
            logger.error(f"AWS Bedrock failed for mirror contract: {e}")
            logger.warning("Generating fallback content...")
            mirror_contract = self._generate_fallback_mirror_contract(
                contract_text, contract_category, user_interests
            )
        
        # File 2: Redline comparison
        redline_prompt = f"""{prompt}

Create a detailed redline comparison (File 2) showing:
- Original text (marked for deletion)
- New text (marked for addition)
- Side-by-side comparison format
Format this as a clean PDF-ready comparison document."""
        
        try:
            redline_comparison = await self.box_service.ask_ai_about_file(
                contract_file_id, redline_prompt
            )
        except Exception as e:
            logger.error(f"AWS Bedrock failed for redline comparison: {e}")
            logger.warning("Generating fallback content...")
            redline_comparison = self._generate_fallback_redline(contract_text, contract_category)
        
        # File 3: Negotiation guide
        negotiation_prompt = f"""{prompt}

Create a comprehensive negotiation guide (File 3) that includes:
1. Summary of all changes made
2. Why each change protects the user's interests
3. Which items are negotiable vs non-negotiable
4. How to present each change to the other party
5. Talking points and rationale for each change
6. Recommended negotiation order
Format this as a clear, actionable guide."""
        
        try:
            negotiation_guide = await self.box_service.ask_ai_about_file(
                contract_file_id, negotiation_prompt
            )
        except Exception as e:
            logger.error(f"AWS Bedrock failed for negotiation guide: {e}")
            logger.warning("Generating fallback content...")
            negotiation_guide = self._generate_fallback_negotiation_guide(
                contract_text, contract_category, user_interests
            )
        
        # Upload the 3 files to Box
        await self._upload_output_files(
            mirror_folder_id,
            contract_name,
            mirror_contract,
            redline_comparison,
            negotiation_guide
        )
    
    def _build_analysis_prompt(
        self,
        contract_text: str,
        user_interests: Optional[str],
        per_contract_instructions: Optional[str],
        contract_category: str
    ) -> str:
        """Build the prompt for Box AI analysis."""
        
        # Check if we have any user guidance
        has_user_guidance = user_interests is not None or per_contract_instructions is not None
        
        if has_user_guidance:
            # User has provided interests/instructions - use them
            prompt = f"""You are a contract analysis expert. Analyze this {contract_category} and create a protected version that safeguards the user's interests.

CONTRACT TYPE: {contract_category}

CONTRACT TO ANALYZE:
{contract_text[:5000]}... (full contract provided in file)
"""
            
            if user_interests:
                prompt += f"""

USER'S GENERAL INTERESTS:
{user_interests}
"""
            
            if per_contract_instructions:
                prompt += f"""

SPECIFIC INSTRUCTIONS FOR THIS CONTRACT:
{per_contract_instructions}

NOTE: Per-contract instructions take priority over general interests.
"""
            
            prompt += f"""

TASK:
1. Identify terms that need to be changed to protect the user's interests
2. Identify non-negotiable terms that must stay exactly as-is
3. Rewrite the contract protecting user interests while maintaining fairness
4. Create a comparison showing all changes
5. Provide negotiation guidance

GUIDELINES:
- Keep non-negotiables exactly as specified
- Make changes that protect user interests while being fair
- Maintain professional tone and legal accuracy
- Ensure changes are reasonable and defensible
- Consider {contract_category} specific concerns and industry standards
"""
        else:
            # No user guidance - make contract fairer without changing non-negotiables
            prompt = f"""You are a contract analysis expert. Analyze this {contract_category} and create a fairer, more balanced version.

CONTRACT TYPE: {contract_category}

CONTRACT TO ANALYZE:
{contract_text[:5000]}... (full contract provided in file)

TASK:
1. Identify terms that are one-sided, unfair, or could be improved for balance
2. Identify non-negotiable terms (core business terms, pricing, deliverables) that must stay exactly as-is
3. Rewrite the contract to make it fairer and more balanced while keeping non-negotiables intact
4. Create a comparison showing all changes
5. Provide guidance on the improvements made

GUIDELINES:
- DO NOT change non-negotiable terms (core business terms, pricing, deliverables, key obligations)
- Make the contract more balanced and fair for both parties
- Improve clarity, add reasonable protections, ensure mutual obligations
- Add fair termination clauses, reasonable notice periods, balanced liability terms
- Maintain professional tone and legal accuracy
- Ensure changes are reasonable and industry-standard
- Consider {contract_category} specific best practices and industry standards
- Focus on making the contract more equitable without altering core business terms
"""
        
        return prompt
    
    def _generate_fallback_mirror_contract(
        self, contract_text: str, contract_category: str, user_interests: Optional[str]
    ) -> str:
        """Generate a fallback mirror contract when Box AI is unavailable."""
        return f"""MIRROR CONTRACT - PROTECTING YOUR INTERESTS
===========================================

Contract Type: {contract_category}

NOTE: This is a placeholder document. Box AI is currently unavailable.
Please review the original contract and apply your interests manually.

Original Contract:
{contract_text[:2000]}...

Your Interests:
{user_interests if user_interests else "No specific interests provided"}

RECOMMENDATIONS:
1. Review the original contract carefully
2. Identify terms that need modification based on your interests
3. Consult with a legal professional for contract modifications
4. Ensure all changes protect your interests while maintaining fairness

This document will be replaced with AI-generated content once Box AI permissions are configured.
"""
    
    def _generate_fallback_redline(self, contract_text: str, contract_category: str) -> str:
        """Generate a fallback redline comparison when Box AI is unavailable."""
        return f"""REDLINE COMPARISON DOCUMENT
============================

Contract Type: {contract_category}

NOTE: This is a placeholder document. Box AI is currently unavailable.

Original Contract Excerpt:
{contract_text[:1000]}...

REDLINE COMPARISON:
-------------------
[Original Text] → [Suggested Changes]

This document will show side-by-side comparisons of:
- Original contract terms
- Suggested modifications
- Rationale for each change

This document will be replaced with AI-generated content once Box AI permissions are configured.
"""
    
    def _generate_fallback_negotiation_guide(
        self, contract_text: str, contract_category: str, user_interests: Optional[str]
    ) -> str:
        """Generate a fallback negotiation guide when Box AI is unavailable."""
        return f"""NEGOTIATION GUIDE
==================

Contract Type: {contract_category}

NOTE: This is a placeholder document. Box AI is currently unavailable.

Your Interests:
{user_interests if user_interests else "No specific interests provided"}

NEGOTIATION STRATEGY:
--------------------
1. Review all contract terms carefully
2. Identify key areas that need modification
3. Prioritize changes based on your interests
4. Prepare talking points for each change
5. Be ready to compromise on non-critical terms

KEY AREAS TO REVIEW:
- Termination clauses
- Payment terms
- Liability and indemnification
- Intellectual property rights
- Non-compete clauses (if applicable)
- Dispute resolution

This document will be replaced with AI-generated content once Box AI permissions are configured.
"""
    
    async def _upload_output_files(
        self,
        mirror_folder_id: str,
        contract_name: str,
        mirror_contract: str,
        redline_comparison: str,
        negotiation_guide: str
    ):
        """Upload the 3 output files to Box as plain text files."""
        
        # File 1: Mirror contract (TXT)
        await self.box_service.upload_text_file(
            mirror_folder_id,
            f"1_mirror_contract_protecting_YOUR_interests.txt",
            mirror_contract
        )
        
        # File 2: Redline comparison (TXT)
        await self.box_service.upload_text_file(
            mirror_folder_id,
            f"2_clean_redline_comparison.txt",
            redline_comparison
        )
        
        # File 3: Negotiation guide (TXT)
        await self.box_service.upload_text_file(
            mirror_folder_id,
            f"3_negotiation_guide.txt",
            negotiation_guide
        )
        
        logger.info(f"Uploaded 3 plain text output files for {contract_name}")
    
    async def run_continuous_monitoring(self, check_interval: int = 60, action_item_check_interval: int = 3600):
        """Continuously monitor for new contracts and check for action items."""
        logger.info(f"Starting continuous monitoring (checking contracts every {check_interval}s)")
        logger.info(f"Checking action items every {action_item_check_interval}s ({action_item_check_interval/60} minutes)")
        
        last_action_item_check = time.time()
        iteration_count = 0
        iterations_per_action_check = action_item_check_interval // check_interval
        
        while True:
            try:
                iteration_count += 1
                
                # Check for new contracts
                await self.process_new_contracts()
                
                # Check for action items periodically
                if iteration_count >= iterations_per_action_check:
                    await self.check_all_contracts_for_action_items()
                    iteration_count = 0
                    last_action_item_check = time.time()
                
                await asyncio.sleep(check_interval)
            except KeyboardInterrupt:
                logger.info("Stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(check_interval)


async def main():
    """Main entry point."""
    processor = ContractProcessor()
    
    try:
        await processor.initialize()
        
        # Process any existing contracts first
        await processor.process_new_contracts()
        
        # Check for action items on startup
        await processor.check_all_contracts_for_action_items()
        
        # Start continuous monitoring
        # Check for new contracts every 3 seconds (for faster testing)
        # Check for action items every hour (3600 seconds)
        await processor.run_continuous_monitoring(
            check_interval=3,
            action_item_check_interval=3600
        )
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

