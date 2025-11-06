"""
OASIS+ Integration Service
Automated UI interaction with legacy OASIS+ system
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logger = logging.getLogger(__name__)


class OASISClient:
    """
    Client for automating interactions with OASIS+ legacy system
    
    OASIS+ System Details:
    - URL: http://128.1.1.185/prod/faces/Home
    - Protocol: HTTP (internal network)
    - Platform: Oracle Faces (JSF-based)
    """
    
    def __init__(
        self,
        base_url: str = "http://128.1.1.185/prod/faces/Home",
        username: str = "U29958",
        password: str = "U29958",
        headless: bool = True
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.authenticated = False
    
    async def initialize(self):
        """Initialize browser and navigate to OASIS+"""
        try:
            playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            logger.info("✓ Browser initialized")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize browser: {e}")
            return False
    
    async def authenticate(self) -> bool:
        """
        Authenticate with OASIS+ system
        
        Returns:
            bool: True if authentication successful
        """
        try:
            if not self.page:
                await self.initialize()
            
            logger.info(f"Navigating to OASIS+: {self.base_url}")
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            
            # Wait for login form to load
            await self.page.wait_for_selector('input[type="text"]', timeout=10000)
            
            # Fill username
            await self.page.fill('input[type="text"]', self.username)
            logger.info(f"✓ Username entered: {self.username}")
            
            # Fill password
            await self.page.fill('input[type="password"]', self.password)
            logger.info("✓ Password entered")
            
            # Click login button
            await self.page.click('button[type="submit"], input[type="submit"]')
            
            # Wait for navigation after login
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            
            # Verify login success by checking for expected elements
            current_url = self.page.url
            if 'login' not in current_url.lower() and 'error' not in current_url.lower():
                self.authenticated = True
                logger.info("✓ Authentication successful")
                return True
            else:
                logger.error("✗ Authentication failed - still on login page")
                return False
                
        except Exception as e:
            logger.exception(f"✗ Authentication error: {e}")
            return False
    
    async def submit_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a claim to OASIS+ system
        
        Args:
            claim_data: Dictionary containing claim information
                - patient_id: str
                - claim_number: str
                - service_date: str (YYYY-MM-DD)
                - payer: str
                - diagnosis_codes: list[str]
                - procedure_codes: list[str]
                - total_amount: float
        
        Returns:
            Dictionary with submission result
        """
        try:
            if not self.authenticated:
                auth_success = await self.authenticate()
                if not auth_success:
                    return {
                        "success": False,
                        "error": "Authentication failed",
                        "timestamp": datetime.now().isoformat()
                    }
            
            logger.info(f"Submitting claim: {claim_data.get('claim_number')}")
            
            # Navigate to claim submission page
            # TODO: Update selectors based on actual OASIS+ UI
            await self.page.click('text=New Claim')
            await self.page.wait_for_load_state('networkidle')
            
            # Fill patient information
            await self.page.fill('#patientId', claim_data['patient_id'])
            await self.page.fill('#claimNumber', claim_data['claim_number'])
            
            # Fill service date
            await self.page.fill('#serviceDate', claim_data['service_date'])
            
            # Select payer
            await self.page.select_option('#payer', claim_data['payer'])
            
            # Fill diagnosis codes
            for idx, icd_code in enumerate(claim_data['diagnosis_codes']):
                await self.page.fill(f'#diagnosisCode{idx + 1}', icd_code)
            
            # Fill procedure codes
            for idx, cpt_code in enumerate(claim_data['procedure_codes']):
                await self.page.fill(f'#procedureCode{idx + 1}', cpt_code)
            
            # Fill amount
            await self.page.fill('#totalAmount', str(claim_data['total_amount']))
            
            # Take screenshot before submission (for audit)
            screenshot_path = f"claim_{claim_data['claim_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.page.screenshot(path=screenshot_path)
            
            # Submit the form
            await self.page.click('button[type="submit"]')
            
            # Wait for confirmation
            await self.page.wait_for_selector('.success-message, .confirmation', timeout=15000)
            
            # Extract confirmation number
            confirmation_element = await self.page.query_selector('.confirmation-number')
            confirmation_number = await confirmation_element.inner_text() if confirmation_element else "N/A"
            
            logger.info(f"✓ Claim submitted successfully: {confirmation_number}")
            
            return {
                "success": True,
                "confirmation_number": confirmation_number,
                "claim_number": claim_data['claim_number'],
                "screenshot": screenshot_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"✗ Claim submission error: {e}")
            
            # Take error screenshot
            if self.page:
                error_screenshot = f"error_{claim_data.get('claim_number', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=error_screenshot)
            
            return {
                "success": False,
                "error": str(e),
                "claim_number": claim_data.get('claim_number'),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_claim_status(self, claim_number: str) -> Dict[str, Any]:
        """
        Retrieve claim status from OASIS+ system
        
        Args:
            claim_number: Claim number to check
        
        Returns:
            Dictionary with claim status information
        """
        try:
            if not self.authenticated:
                auth_success = await self.authenticate()
                if not auth_success:
                    return {"success": False, "error": "Authentication failed"}
            
            # Navigate to claim search
            await self.page.click('text=Search Claims')
            await self.page.wait_for_load_state('networkidle')
            
            # Search for claim
            await self.page.fill('#claimSearch', claim_number)
            await self.page.click('button[type="search"]')
            
            # Wait for results
            await self.page.wait_for_selector('.claim-result', timeout=10000)
            
            # Extract status
            status_element = await self.page.query_selector('.claim-status')
            status = await status_element.inner_text() if status_element else "UNKNOWN"
            
            return {
                "success": True,
                "claim_number": claim_number,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"✗ Status check error: {e}")
            return {
                "success": False,
                "error": str(e),
                "claim_number": claim_number
            }
    
    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            logger.info("✓ Browser closed")
            
        except Exception as e:
            logger.error(f"✗ Error closing browser: {e}")


# FastAPI service wrapper
if __name__ == "__main__":
    import asyncio
    
    async def test_oasis_client():
        """Test OASIS+ client"""
        client = OASISClient(headless=False)
        
        try:
            # Initialize and authenticate
            await client.initialize()
            success = await client.authenticate()
            
            if success:
                print("✓ Authentication successful!")
                
                # Test claim submission
                test_claim = {
                    "patient_id": "1234567890",
                    "claim_number": "TEST-001",
                    "service_date": "2024-01-20",
                    "payer": "PAYER_A",
                    "diagnosis_codes": ["J45.0"],
                    "procedure_codes": ["99213"],
                    "total_amount": 500.00
                }
                
                result = await client.submit_claim(test_claim)
                print(f"Submission result: {result}")
            else:
                print("✗ Authentication failed")
        
        finally:
            await client.close()
    
    # Run test
    asyncio.run(test_oasis_client())
