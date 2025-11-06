"""
Tawuniya/Waseel Provider Portal and API Automation
Handles both Waseel API integration and web portal automation for Tawuniya claims
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

import aiohttp
import requests
from playwright.async_api import async_playwright, Page, Browser


class WaseelPortalBot:
    """Automation bot for Waseel/Tawuniya provider portal and API"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # API endpoints
        self.base_url = "https://jisr.waseel.com"
        self.api_base_url = "https://api.waseel.com"
        self.auth_base_url = "https://iam.waseel.com"
        
        # OAuth/OIDC settings
        self.client_id = os.getenv("WASEEL_CLIENT_ID")
        self.client_secret = os.getenv("WASEEL_CLIENT_SECRET")
        self.redirect_uri = os.getenv("WASEEL_REDIRECT_URI", "https://claimlinc.brainsait.io/callback")
        
        # Token storage
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Download directory
        self.download_dir = Path("./downloads/waseel")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
        
    async def start(self):
        """Start the browser for web automation"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
    async def stop(self):
        """Close browser and page"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
    
    async def authenticate(self) -> bool:
        """Authenticate using OAuth2/OIDC flow"""
        try:
            if self.client_id and self.client_secret:
                return await self._api_authenticate()
            else:
                return await self._web_authenticate()
        except Exception as e:
            print(f"❌ Waseel authentication error: {str(e)}")
            return False
    
    async def _api_authenticate(self) -> bool:
        """Authenticate using OAuth2 client credentials"""
        try:
            auth_url = f"{self.auth_base_url}/realms/waseel-prod/protocol/openid-connect/token"
            
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get("access_token")
                        expires_in = token_data.get("expires_in", 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        print("✅ Waseel API authentication successful")
                        return True
                    else:
                        print(f"❌ API authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ API authentication error: {str(e)}")
            return False
    
    async def _web_authenticate(self) -> bool:
        """Authenticate using web login flow"""
        try:
            # Navigate to Waseel login
            login_url = f"{self.base_url}/login"
            await self.page.goto(login_url, wait_until="networkidle")
            
            # Wait for login form
            await self.page.wait_for_selector("#username", timeout=30000)
            
            # Fill credentials (using environment variables)
            username = os.getenv("WASEEL_USERNAME")
            password = os.getenv("WASEEL_PASSWORD")
            
            if not username or not password:
                print("❌ Missing WASEEL_USERNAME or WASEEL_PASSWORD environment variables")
                return False
                
            await self.page.fill("#username", username)
            await self.page.fill("#password", password)
            
            # Handle potential 2FA
            try:
                await self.page.click("#kc-login")
                await self.page.wait_for_load_state("networkidle")
                
                # Check for 2FA prompt
                twofa_selectors = [
                    "#otp",
                    "#verification-code",
                    "input[name='code']",
                    ".two-factor"
                ]
                
                for selector in twofa_selectors:
                    try:
                        otp_input = await self.page.query_selector(selector)
                        if otp_input:
                            print("🔐 2FA required - please provide OTP manually")
                            await self.page.wait_for_timeout(30000)  # Wait for manual input
                            break
                    except:
                        continue
                        
                print("✅ Waseel web authentication successful")
                return True
                
            except Exception as e:
                print(f"❌ Web authentication error: {str(e)}")
                return False
                
        except Exception as e:
            print(f"❌ Web authentication error: {str(e)}")
            return False
    
    async def submit_claim_via_api(self, claim_data: Dict[str, Any]) -> Optional[str]:
        """Submit claim using Waseel API"""
        try:
            if not self.access_token:
                if not await self.authenticate():
                    return None
                    
            # Convert claim data to FHIR format if needed
            fhir_claim = await self._convert_to_fhir_claim(claim_data)
            
            api_url = f"{self.api_base_url}/nphies/claims"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/fhir+json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=fhir_claim, headers=headers) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        submission_id = result.get("id")
                        print(f"✅ Claim submitted via API: {submission_id}")
                        return submission_id
                    else:
                        error_text = await response.text()
                        print(f"❌ API submission failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"❌ API submission error: {str(e)}")
            return None
    
    async def submit_claim_via_portal(self, file_path: str) -> Optional[str]:
        """Submit claim via web portal"""
        try:
            if not self.page:
                await self.start()
                
            # Navigate to claims submission
            await self.navigate_to_claims_section()
            
            # Upload file
            file_input = await self.page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(str(Path(file_path).absolute()))
                await self.page.wait_for_timeout(2000)
                
                # Submit form
                submit_btn = await self.page.query_selector("input[type='submit'], button[type='submit']")
                if submit_btn:
                    await submit_btn.click()
                    await self.page.wait_for_load_state("networkidle")
                    
                    # Look for confirmation
                    await self.page.wait_for_timeout(5000)
                    confirmation_text = await self.page.text_content("body")
                    
                    # Extract submission ID
                    import re
                    id_match = re.search(r'[A-Z]{2,3}-\d+', confirmation_text)
                    if id_match:
                        submission_id = id_match.group()
                        print(f"✅ Claim submitted via portal: {submission_id}")
                        return submission_id
                        
            return None
            
        except Exception as e:
            print(f"❌ Portal submission error: {str(e)}")
            return None
    
    async def navigate_to_claims_section(self) -> bool:
        """Navigate to claims section in web portal"""
        try:
            claims_links = [
                "Claims",
                "Submit Claims",
                "New Claim",
                "Create Claim"
            ]
            
            for link_text in claims_links:
                try:
                    link = await self.page.query_selector(f"text='{link_text}'")
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            return False
    
    async def check_claim_status_api(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Check claim status using API"""
        try:
            if not self.access_token:
                if not await self.authenticate():
                    return None
                    
            api_url = f"{self.api_base_url}/nphies/claims/{submission_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        claim_data = await response.json()
                        status_info = {
                            "submission_id": submission_id,
                            "status": claim_data.get("status"),
                            "amount": claim_data.get("total", {}).get("value"),
                            "processing_date": claim_data.get("created"),
                            "insurance_payment": claim_data.get("insurance", [{}])[0].get("item") if claim_data.get("insurance") else None
                        }
                        return status_info
                    else:
                        print(f"❌ Status check API failed: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Status check API error: {str(e)}")
            return None
    
    async def get_rejected_claims_api(self) -> Optional[List[Dict[str, Any]]]:
        """Get list of rejected claims via API"""
        try:
            if not self.access_token:
                if not await self.authenticate():
                    return None
                    
            # Search for rejected claims
            api_url = f"{self.api_base_url}/nphies/claims"
            params = {
                "status": "rejected",
                "_count": "100"
            }
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        bundle = await response.json()
                        claims = []
                        
                        for entry in bundle.get("entry", []):
                            if "resource" in entry:
                                resource = entry["resource"]
                                claims.append({
                                    "id": resource.get("id"),
                                    "status": resource.get("status"),
                                    "patient": resource.get("patient", {}).get("display"),
                                    "amount": resource.get("total", {}).get("value"),
                                    "created": resource.get("created"),
                                    "provider": resource.get("provider", {}).get("display")
                                })
                        
                        print(f"✅ Retrieved {len(claims)} rejected claims")
                        return claims
                    else:
                        print(f"❌ Get rejected claims API failed: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Get rejected claims error: {str(e)}")
            return None
    
    async def move_claim_to_ready_state(self, claim_id: str) -> bool:
        """Move rejected claim back to ready state for resubmission"""
        try:
            if not self.access_token:
                if not await self.authenticate():
                    return False
                    
            api_url = f"{self.api_base_url}/nphies/claims/{claim_id}/move-to-ready"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers) as response:
                    if response.status in [200, 204]:
                        print(f"✅ Claim {claim_id} moved to ready state")
                        return True
                    else:
                        print(f"❌ Move to ready failed: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Move to ready error: {str(e)}")
            return False
    
    async def download_rejection_report_api(self) -> Optional[str]:
        """Download rejection report via API"""
        try:
            if not self.access_token:
                if not await self.authenticate():
                    return None
                    
            # Get report endpoint
            api_url = f"{self.api_base_url}/nphies/reports/rejections"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        filename = f"waseel_rejections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        filepath = self.download_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(await response.read())
                            
                        print(f"✅ Downloaded rejection report: {filepath}")
                        return str(filepath)
                    else:
                        print(f"❌ Download report API failed: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Download report error: {str(e)}")
            return None
    
    async def _convert_to_fhir_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert claim data to FHIR format"""
        try:
            # Basic FHIR Claim structure
            fhir_claim = {
                "resourceType": "Claim",
                "id": claim_data.get("claimId"),
                "status": "active",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                            "code": "institutional"
                        }
                    ]
                },
                "patient": {
                    "reference": f"Patient/{claim_data.get('patientId')}",
                    "display": claim_data.get("patientName", "Unknown")
                },
                "provider": {
                    "reference": f"Organization/{claim_data.get('providerCode')}",
                    "display": claim_data.get("providerName", "Unknown Provider")
                },
                "created": datetime.now().isoformat() + "Z",
                "total": {
                    "value": float(claim_data.get("amount", 0)),
                    "currency": "SAR"
                }
            }
            
            # Add diagnosis information
            if claim_data.get("diagnosisCodes"):
                fhir_claim["diagnosis"] = []
                for i, code in enumerate(claim_data["diagnosisCodes"]):
                    fhir_claim["diagnosis"].append({
                        "sequence": i + 1,
                        "diagnosisCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/sid/icd-10",
                                    "code": code
                                }
                            ]
                        }
                    })
            
            # Add procedure information
            if claim_data.get("procedureCodes"):
                fhir_claim["procedure"] = []
                for i, code in enumerate(claim_data["procedureCodes"]):
                    fhir_claim["procedure"].append({
                        "sequence": i + 1,
                        "procedureCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://www.ama-assn.org/go/cpt",
                                    "code": code
                                }
                            ]
                        }
                    })
            
            # Add insurance information
            fhir_claim["insurance"] = [
                {
                    "sequence": 1,
                    "focal": True,
                    "coverage": {
                        "reference": f"Coverage/{claim_data.get('policyNumber')}",
                        "display": "Tawuniya Insurance"
                    }
                }
            ]
            
            return fhir_claim
            
        except Exception as e:
            print(f"❌ FHIR conversion error: {str(e)}")
            return {}
    
    async def logout(self):
        """Logout from the system"""
        try:
            if self.page:
                await self.page.goto(f"{self.base_url}/logout")
                print("✅ Logged out successfully")
            
            # Clear tokens
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            
        except Exception as e:
            print(f"❌ Logout error: {str(e)}")


# Test function
async def test_waseel_integration():
    """Test function for Waseel integration"""
    async with WaseelPortalBot(headless=False) as bot:
        # Test authentication
        if not await bot.authenticate():
            print("❌ Authentication failed")
            return
            
        # Load sample claim data
        sample_file = Path("../sample-data/waseel-claim-sample.json")
        if sample_file.exists():
            with open(sample_file) as f:
                claim_data = json.load(f)
                
            # Test API submission
            submission_id = await bot.submit_claim_via_api(claim_data)
            if submission_id:
                # Test status check
                status = await bot.check_claim_status_api(submission_id)
                print(f"Claim status: {status}")
                
                # Test getting rejected claims
                rejected_claims = await bot.get_rejected_claims_api()
                if rejected_claims:
                    print(f"Found {len(rejected_claims)} rejected claims")
                    
                    # Test moving claim to ready state
                    if rejected_claims:
                        claim_id = rejected_claims[0]["id"]
                        await bot.move_claim_to_ready_state(claim_id)
        
        # Keep browser open for inspection
        await bot.page.wait_for_timeout(10000)


if __name__ == "__main__":
    asyncio.run(test_waseel_integration())
