"""
GlobeMed Saudi Provider Portal Automation using Playwright
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser
from typing import Optional, Dict, Any


class GlobeMedPortalBot:
    """Automation bot for GlobeMed Saudi provider portal"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.base_url = "https://e-claims.globemedsaudi.com"
        self.download_dir = Path("./downloads/globemed")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
        
    async def start(self):
        """Start the browser and create new page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        self.page = await self.browser.new_page()
        
        # Set viewport and user agent
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    async def stop(self):
        """Close browser and page"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
            
    async def login(self, username: str, password: str) -> bool:
        """Login to GlobeMed provider portal"""
        try:
            # Navigate to login page
            login_url = f"{self.base_url}/login.html"
            await self.page.goto(login_url, wait_until="networkidle")
            
            # Wait for login form elements
            await self.page.wait_for_selector("input[name='username']", timeout=30000)
            await self.page.wait_for_selector("input[name='password']", timeout=30000)
            
            # Fill in credentials
            await self.page.fill("input[name='username']", username)
            await self.page.fill("input[name='password']", password)
            
            # Click login button
            login_button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "#loginBtn",
                ".login-btn"
            ]
            
            for selector in login_button_selectors:
                try:
                    login_btn = await self.page.query_selector(selector)
                    if login_btn:
                        await login_btn.click()
                        break
                except:
                    continue
                    
            # Wait for navigation or error message
            try:
                # Wait for successful login (check for dashboard or home page)
                await self.page.wait_for_selector("#mainContent", timeout=10000)
                print("✅ GlobeMed login successful")
                return True
            except:
                # Check for error message
                error_selectors = [
                    ".error-message",
                    "#errorMsg",
                    ".alert-danger",
                    "p:has-text('Invalid')"
                ]
                
                for selector in error_selectors:
                    try:
                        error_element = await self.page.query_selector(selector)
                        if error_element:
                            error_text = await error_element.text_content()
                            print(f"❌ GlobeMed login failed: {error_text}")
                            return False
                    except:
                        continue
                        
                print("❌ GlobeMed login failed: Unknown error")
                return False
                
        except Exception as e:
            print(f"❌ GlobeMed login error: {str(e)}")
            return False
            
    async def navigate_to_claims_section(self) -> bool:
        """Navigate to claims submission section"""
        try:
            # Look for claims menu or links
            claims_links = [
                "Claims",
                "Submit Claims",
                "Claims Submission",
                "New Claim",
                "Create Claim"
            ]
            
            for link_text in claims_links:
                try:
                    # Try different ways to find the link
                    link = await self.page.query_selector(f"a:has-text('{link_text}')")
                    if not link:
                        link = await self.page.query_selector(f"button:has-text('{link_text}')")
                    if not link:
                        link = await self.page.query_selector(f"li:has-text('{link_text}')")
                    
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        print(f"✅ Navigated to {link_text} section")
                        return True
                except:
                    continue
                    
            # Try navigation menu approach
            try:
                menu_links = await self.page.query_selector_all(".nav-link, .menu-item, .dropdown-toggle")
                for menu_link in menu_links:
                    text = await menu_link.text_content()
                    if text and "claim" in text.lower():
                        await menu_link.click()
                        await self.page.wait_for_load_state("networkidle")
                        print(f"✅ Navigated via menu to claims section")
                        return True
            except:
                pass
                
            print("❌ Could not find claims section")
            return False
            
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            return False
            
    async def upload_claim_file(self, file_path: str) -> Optional[str]:
        """Upload claim file to GlobeMed portal"""
        try:
            # Wait for file upload input
            upload_selectors = [
                "input[type='file']",
                "#fileUpload",
                "#fileInput",
                ".file-upload-input",
                "input[name='file']"
            ]
            
            file_input = None
            for selector in upload_selectors:
                try:
                    file_input = await self.page.query_selector(selector)
                    if file_input:
                        break
                except:
                    continue
                    
            if not file_input:
                print("❌ Could not find file upload input")
                return None
                
            # Set file path
            absolute_file_path = str(Path(file_path).absolute())
            await file_input.set_input_files(absolute_file_path)
            
            # Wait for file to be selected
            await self.page.wait_for_timeout(2000)
            
            # Click upload/submit button
            upload_buttons = [
                "input[type='submit']",
                "button[type='submit']",
                "#uploadBtn",
                "#submitBtn",
                ".upload-btn",
                ".submit-btn"
            ]
            
            for button_selector in upload_buttons:
                try:
                    submit_btn = await self.page.query_selector(button_selector)
                    if submit_btn:
                        await submit_btn.click()
                        await self.page.wait_for_load_state("networkidle")
                        break
                except:
                    continue
                    
            # Wait for upload confirmation
            await self.page.wait_for_timeout(5000)
            
            # Look for confirmation message or submission ID
            confirmation_selectors = [
                ".success-message",
                "#successMsg",
                "#confirmation",
                ".alert-success",
                "p:has-text('success')",
                "p:has-text('submitted')"
            ]
            
            submission_id = None
            for selector in confirmation_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        text_content = await element.text_content()
                        if text_content and any(keyword in text_content.lower() for keyword in ["success", "submitted", "confirmation", "id"]):
                            # Extract submission ID if present
                            import re
                            id_match = re.search(r'[A-Z]{2,3}-\d+', text_content)
                            if id_match:
                                submission_id = id_match.group()
                            print(f"✅ File uploaded successfully: {text_content}")
                            return submission_id
                except:
                    continue
                    
            # If no confirmation message found, check URL or page title
            current_url = self.page.url
            if "success" in current_url or "confirmation" in current_url:
                print("✅ File upload completed (URL indicates success)")
                return submission_id
                
            print("✅ File upload completed")
            return submission_id
            
        except Exception as e:
            print(f"❌ File upload error: {str(e)}")
            return None
            
    async def check_claim_status(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Check the status of a submitted claim"""
        try:
            # Navigate to claims status section
            status_links = [
                "Claims Status", 
                "Status", 
                "View Claims", 
                "Track Claims",
                "Claim Tracking"
            ]
            
            for link_text in status_links:
                try:
                    link = await self.page.query_selector(f"text='{link_text}'")
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        break
                except:
                    continue
                    
            # Search for the submission ID
            search_selectors = [
                "#searchInput",
                "#txtSearch",
                "input[name='search']",
                "input[placeholder*='search']",
                "input[placeholder*='Search']"
            ]
            
            for selector in search_selectors:
                try:
                    search_input = await self.page.query_selector(selector)
                    if search_input:
                        await search_input.fill(submission_id)
                        
                        # Click search button if exists
                        search_button_selectors = [
                            "#searchBtn",
                            "#btnSearch",
                            "button[type='submit']"
                        ]
                        
                        for button_selector in search_button_selectors:
                            try:
                                search_btn = await self.page.query_selector(button_selector)
                                if search_btn:
                                    await search_btn.click()
                                    await self.page.wait_for_load_state("networkidle")
                                    break
                            except:
                                continue
                        break
                except:
                    continue
                
            # Extract status information
            status_info = {
                "submission_id": submission_id,
                "status": "Unknown",
                "amount": None,
                "processing_date": None,
                "notes": None,
                "response_time": None
            }
            
            # Look for status table or cards
            table_selectors = [
                ".status-table",
                ".claims-table",
                "#claimsTable",
                "table"
            ]
            
            for selector in table_selectors:
                table = await self.page.query_selector(selector)
                if table:
                    # Extract table data
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        cells = await row.query_selector_all("td, th")
                        if cells:
                            cell_texts = [await cell.text_content() for cell in cells]
                            # Look for submission ID match
                            for i, cell_text in enumerate(cell_texts):
                                if submission_id in cell_text:
                                    # Extract status from next cell
                                    if i + 1 < len(cell_texts):
                                        status_info["status"] = cell_texts[i + 1]
                                    # Extract amount if present
                                    for j, text in enumerate(cell_texts):
                                        if "SAR" in text or "amount" in text.lower():
                                            status_info["amount"] = text
                                            break
                                    return status_info
                                    
            # Alternative: look for status cards or panels
            status_cards = await self.page.query_selector_all(".status-card, .claim-card, .info-box")
            for card in status_cards:
                card_text = await card.text_content()
                if submission_id in card_text:
                    # Extract status information from card text
                    lines = card_text.split('\n')
                    for line in lines:
                        if "status" in line.lower():
                            status_info["status"] = line.split(':')[1].strip() if ':' in line else "Found"
                        if "amount" in line.lower() or "SAR" in line:
                            status_info["amount"] = line.strip()
                    break
                    
            return status_info
            
        except Exception as e:
            print(f"❌ Status check error: {str(e)}")
            return None
            
    async def download_rejection_report(self) -> Optional[str]:
        """Download rejection report if available"""
        try:
            # Navigate to reports or rejection section
            report_links = [
                "Reports", 
                "Rejections", 
                "Download Reports",
                "Export Reports",
                "Reports & Analytics"
            ]
            
            for link_text in report_links:
                try:
                    link = await self.page.query_selector(f"text='{link_text}'")
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        break
                except:
                    continue
                    
            # Look for rejection or export options
            export_selectors = [
                ".export-rejections",
                "button:has-text('Export')",
                "a:has-text('Download')",
                ".download-rejections",
                "#exportRejections",
                "#downloadRejections"
            ]
            
            for selector in export_selectors:
                export_element = await self.page.query_selector(selector)
                if export_element:
                    # Set up download handler
                    filename = f"globemed_rejection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    filepath = self.download_dir / filename
                    
                    async with self.page.expect_download() as download_info:
                        await export_element.click()
                        download = await download_info.value
                        await download.save_as(filepath)
                        
                    print(f"✅ Downloaded rejection report: {filepath}")
                    return str(filepath)
                    
            # Alternative: look for specific rejection report links
            rejection_links = await self.page.query_selector_all("a[href*='rejection'], a[href*='export']")
            for link in rejection_links:
                href = await link.get_attribute('href')
                if href and ("rejection" in href.lower() or "export" in href.lower()):
                    filename = f"globemed_rejection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    filepath = self.download_dir / filename
                    
                    async with self.page.expect_download() as download_info:
                        await link.click()
                        download = await download_info.value
                        await download.save_as(filepath)
                        
                    print(f"✅ Downloaded rejection report: {filepath}")
                    return str(filepath)
                    
            print("❌ No rejection report found for download")
            return None
            
        except Exception as e:
            print(f"❌ Download error: {str(e)}")
            return None
            
    async def get_claims_list(self, limit: int = 50) -> Optional[list[Dict[str, Any]]]:
        """Get list of claims from the portal"""
        try:
            claims = []
            
            # Look for claims table
            table_selectors = [
                "#claimsTable",
                ".claims-table",
                "table"
            ]
            
            table = None
            for selector in table_selectors:
                table = await self.page.query_selector(selector)
                if table:
                    break
                    
            if not table:
                print("❌ Could not find claims table")
                return None
                
            # Extract claims data
            rows = await table.query_selector_all("tr")
            for row in rows[:limit]:  # Limit number of claims
                cells = await row.query_selector_all("td")
                if len(cells) >= 3:  # Minimum columns
                    cell_texts = [await cell.text_content() for cell in cells]
                    
                    claim_data = {
                        "id": cell_texts[0] if len(cell_texts) > 0 else "",
                        "status": cell_texts[1] if len(cell_texts) > 1 else "",
                        "amount": cell_texts[2] if len(cell_texts) > 2 else "",
                        "date": cell_texts[3] if len(cell_texts) > 3 else "",
                        "patient": cell_texts[4] if len(cell_texts) > 4 else ""
                    }
                    claims.append(claim_data)
                    
            print(f"✅ Retrieved {len(claims)} claims")
            return claims
            
        except Exception as e:
            print(f"❌ Error retrieving claims list: {str(e)}")
            return None
            
    async def logout(self):
        """Logout from the portal"""
        try:
            logout_selectors = [
                "text=Logout",
                "text=Sign Out", 
                "text=Exit",
                "#logoutBtn",
                ".logout-btn"
            ]
            
            for selector in logout_selectors:
                try:
                    link = await self.page.query_selector(selector)
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        print("✅ Logged out successfully")
                        return
                except:
                    continue
                    
            # Alternative: navigate to logout URL
            try:
                await self.page.goto(f"{self.base_url}/logout")
                print("✅ Logged out via URL")
                return
            except:
                pass
                
        except Exception as e:
            print(f"❌ Logout error: {str(e)}")


# Test function for manual testing
async def test_globemed_login_and_upload():
    """Test function for debugging GlobeMed automation"""
    username = os.getenv("GLOBEMED_USERNAME")
    password = os.getenv("GLOBEMED_PASSWORD")
    
    if not username or not password:
        print("❌ Missing GLOBEMED_USERNAME or GLOBEMED_PASSWORD environment variables")
        return
        
    async with GlobeMedPortalBot(headless=False) as bot:
        # Login
        success = await bot.login(username, password)
        if not success:
            print("❌ Login failed, cannot proceed with test")
            return
            
        # Navigate to claims
        await bot.navigate_to_claims_section()
        
        # Test file upload (if sample file exists)
        sample_file = Path("../sample-data/globemed-claim-sample.json")
        if sample_file.exists():
            await bot.upload_claim_file(str(sample_file))
            
        # Get claims list
        # claims = await bot.get_claims_list()
        # print(f"Found {len(claims) if claims else 0} claims")
        
        # Check status (if submission ID available)
        # await bot.check_claim_status("GLB-2025-0001")
        
        # Download rejection report
        # await bot.download_rejection_report()
        
        # Keep browser open for manual inspection
        await bot.page.wait_for_timeout(10000)


if __name__ == "__main__":
    asyncio.run(test_globemed_login_and_upload())
