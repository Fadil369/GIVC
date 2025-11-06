"""
Bupa Arabia Provider Portal Automation using Playwright
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser
from typing import Optional, Dict, Any


class BupaPortalBot:
    """Automation bot for Bupa Arabia provider portal"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.base_url = "https://provider.bupa.com.sa"
        self.download_dir = Path("./downloads/bupa")
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
        """Login to Bupa provider portal"""
        try:
            # Navigate to login page
            login_url = f"{self.base_url}/Provider/Default.aspx"
            await self.page.goto(login_url, wait_until="networkidle")
            
            # Wait for page to load and check if login form exists
            await self.page.wait_for_selector("#txtUserName", timeout=30000)
            
            # Fill in credentials
            await self.page.fill("#txtUserName", username)
            await self.page.fill("#txtPassword", password)
            
            # Click login button
            await self.page.click("#btnLogin")
            
            # Wait for navigation or error message
            try:
                # Wait for successful login (check for dashboard or claims section)
                await self.page.wait_for_selector("#MainContent_lblWelcome", timeout=10000)
                print("✅ Bupa login successful")
                return True
            except:
                # Check for error message
                error_element = await self.page.query_selector("#lblErrorMessage")
                if error_element:
                    error_text = await error_element.text_content()
                    print(f"❌ Bupa login failed: {error_text}")
                else:
                    print("❌ Bupa login failed: Unknown error")
                return False
                
        except Exception as e:
            print(f"❌ Bupa login error: {str(e)}")
            return False
            
    async def navigate_to_claims_section(self) -> bool:
        """Navigate to claims submission section"""
        try:
            # Look for claims menu or link
            claims_links = [
                "Claims",
                "Submit Claims",
                "Claims Submission",
                "New Claim"
            ]
            
            for link_text in claims_links:
                try:
                    link = await self.page.query_selector(f"text='{link_text}'")
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        print(f"✅ Navigated to {link_text} section")
                        return True
                except:
                    continue
                    
            # If direct link not found, try using navigation menu
            try:
                await self.page.click("#MainContent_Menu1")
                await self.page.wait_for_timeout(2000)
                claims_menu = await self.page.query_selector("text=Claims")
                if claims_menu:
                    await claims_menu.click()
                    await self.page.wait_for_load_state("networkidle")
                    return True
            except:
                pass
                
            print("❌ Could not find claims section")
            return False
            
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            return False
            
    async def upload_claim_file(self, file_path: str) -> Optional[str]:
        """Upload claim file to Bupa portal"""
        try:
            # Wait for file upload input
            upload_inputs = [
                "#FileUpload1",
                "#fileUpload",
                "input[type='file']",
                "#uploadFile"
            ]
            
            file_input = None
            for selector in upload_inputs:
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
            
            # Click upload/submit button
            upload_buttons = [
                "#btnUpload",
                "#btnSubmit",
                "#btnSend",
                "input[type='submit']"
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
                "#lblConfirmation",
                "#lblSuccessMessage",
                "#lblSubmissionID",
                ".success-message",
                ".confirmation"
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
                    
            print("✅ File upload completed")
            return submission_id
            
        except Exception as e:
            print(f"❌ File upload error: {str(e)}")
            return None
            
    async def check_claim_status(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Check the status of a submitted claim"""
        try:
            # Navigate to claims status section
            status_links = ["Claims Status", "Status", "View Claims"]
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
            search_input = await self.page.query_selector("#txtSearch")
            if search_input:
                await search_input.fill(submission_id)
                await self.page.click("#btnSearch")
                await self.page.wait_for_load_state("networkidle")
                
            # Extract status information
            status_info = {
                "submission_id": submission_id,
                "status": "Unknown",
                "amount": None,
                "processing_date": None,
                "notes": None
            }
            
            # Look for status table or elements
            status_selectors = [
                "#GridView1",
                ".status-table",
                ".claims-table",
                "table"
            ]
            
            for selector in status_selectors:
                table = await self.page.query_selector(selector)
                if table:
                    # Extract table data (simplified extraction)
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        cells = await row.query_selector_all("td")
                        if cells:
                            cell_texts = [await cell.text_content() for cell in cells]
                            if submission_id in cell_texts[0]:
                                status_info["status"] = cell_texts[1] if len(cell_texts) > 1 else "Found"
                                status_info["amount"] = cell_texts[2] if len(cell_texts) > 2 else None
                                break
                                
            return status_info
            
        except Exception as e:
            print(f"❌ Status check error: {str(e)}")
            return None
            
    async def download_rejection_report(self) -> Optional[str]:
        """Download rejection report if available"""
        try:
            # Navigate to reports or rejection section
            report_links = ["Reports", "Rejections", "Download Reports"]
            
            for link_text in report_links:
                try:
                    link = await self.page.query_selector(f"text='{link_text}'")
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        break
                except:
                    continue
                    
            # Look for download links or buttons
            download_selectors = [
                ".download-link",
                "a[href*='download']",
                "button:has-text('Download')"
            ]
            
            for selector in download_selectors:
                download_element = await self.page.query_selector(selector)
                if download_element:
                    # Set up download handler
                    filename = f"bupa_rejection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    filepath = self.download_dir / filename
                    
                    async with self.page.expect_download() as download_info:
                        await download_element.click()
                        download = await download_info.value
                        await download.save_as(filepath)
                        
                    print(f"✅ Downloaded rejection report: {filepath}")
                    return str(filepath)
                    
            print("❌ No rejection report found for download")
            return None
            
        except Exception as e:
            print(f"❌ Download error: {str(e)}")
            return None
            
    async def logout(self):
        """Logout from the portal"""
        try:
            logout_links = ["Logout", "Sign Out", "Exit"]
            for link_text in logout_links:
                try:
                    link = await self.page.query_selector(f"text='{link_text}'")
                    if link:
                        await link.click()
                        await self.page.wait_for_load_state("networkidle")
                        print("✅ Logged out successfully")
                        return
                except:
                    continue
        except Exception as e:
            print(f"❌ Logout error: {str(e)}")


# Test function for manual testing
async def test_bupa_login_and_upload():
    """Test function for debugging Bupa automation"""
    username = os.getenv("BUPA_USERNAME")
    password = os.getenv("BUPA_PASSWORD")
    
    if not username or not password:
        print("❌ Missing BUPA_USERNAME or BUPA_PASSWORD environment variables")
        return
        
    async with BupaPortalBot(headless=False) as bot:
        # Login
        success = await bot.login(username, password)
        if not success:
            print("❌ Login failed, cannot proceed with test")
            return
            
        # Navigate to claims
        await bot.navigate_to_claims_section()
        
        # Test file upload (if sample file exists)
        sample_file = Path("../sample-data/bupa-claim-sample.json")
        if sample_file.exists():
            await bot.upload_claim_file(str(sample_file))
            
        # Check status (if submission ID available)
        # await bot.check_claim_status("BPA-2025-0001")
        
        # Download rejection report
        # await bot.download_rejection_report()
        
        # Keep browser open for manual inspection
        await bot.page.wait_for_timeout(10000)


if __name__ == "__main__":
    asyncio.run(test_bupa_login_and_upload())
