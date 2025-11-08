"""
ClaimLinc Rejection Sheet Monitor
Extends portal bots to monitor and download rejection sheets from payer portals
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import re

from playwright.async_api import Page, Browser
import aiofiles


class RejectionMonitor:
    """Base class for rejection monitoring across all payers"""

    def __init__(self, page: Page, download_dir: str = "./downloads/rejections"):
        self.page = page
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.detected_rejections = []

    async def monitor_for_rejections(
        self,
        timeout_seconds: int = 300,
        poll_interval: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Monitor portal for new rejection sheets

        Args:
            timeout_seconds: Maximum monitoring duration
            poll_interval: Interval between checks (seconds)

        Returns:
            List of detected rejection files
        """
        start_time = datetime.now()
        detected_files = []

        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            try:
                # Check for rejection files
                files = await self.check_for_rejection_files()

                # Download new files
                for file_info in files:
                    if not self._is_already_downloaded(file_info):
                        file_path = await self.download_rejection_file(file_info)
                        if file_path:
                            detected_files.append({
                                "filename": file_info.get("filename"),
                                "path": str(file_path),
                                "detected_at": datetime.now().isoformat(),
                                "file_info": file_info
                            })
                            self.detected_rejections.append(file_path)

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except Exception as e:
                print(f"⚠️ Error during monitoring: {str(e)}")
                await asyncio.sleep(poll_interval)

        return detected_files

    async def check_for_rejection_files(self) -> List[Dict[str, Any]]:
        """Check for rejection files on current page (override in subclass)"""
        raise NotImplementedError("Subclass must implement check_for_rejection_files")

    async def download_rejection_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """Download rejection file (override in subclass)"""
        raise NotImplementedError("Subclass must implement download_rejection_file")

    def _is_already_downloaded(self, file_info: Dict[str, Any]) -> bool:
        """Check if file was already downloaded"""
        filename = file_info.get("filename", "")
        file_path = self.download_dir / filename

        if file_path.exists():
            # Check if file was downloaded within last hour
            if (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).total_seconds() < 3600:
                return True

        return False

    async def get_rejection_file_list(self) -> List[Dict[str, str]]:
        """Get list of all rejection files on portal"""
        return self.detected_rejections


class BupaRejectionMonitor(RejectionMonitor):
    """Rejection monitor for Bupa Arabia portal"""

    async def check_for_rejection_files(self) -> List[Dict[str, Any]]:
        """
        Check Bupa portal for rejection/EOB files

        Look for:
        - Rejection reports
        - EOB (Explanation of Benefits) files
        - Claim status reports
        """
        files = []

        try:
            # Navigate to reports section if not already there
            reports_section = await self.page.query_selector("text=Reports") or \
                            await self.page.query_selector("text=Download") or \
                            await self.page.query_selector("text=Claim Status")

            if reports_section:
                await reports_section.click()
                await self.page.wait_for_load_state("networkidle")

            # Look for file download links with rejection patterns
            rejection_patterns = [
                r"rejection.*\.xlsx?",
                r"rejection.*\.csv",
                r"eob.*\.xlsx?",
                r"claim.*response.*\.xlsx?",
                r"denial.*\.xlsx?",
                r"refusal.*\.xlsx?"
            ]

            # Get all downloadable elements
            all_links = await self.page.query_selector_all("a[href*='.xls'], a[href*='.xlsx'], a[href*='.csv']")

            for link in all_links:
                href = await link.get_attribute("href")
                text = await link.text_content()

                if href and any(re.search(pattern, href.lower()) or re.search(pattern, text.lower()) for pattern in rejection_patterns):
                    filename = Path(href).name or f"bupa_rejection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

                    files.append({
                        "filename": filename,
                        "href": href,
                        "text": text,
                        "payer": "Bupa Arabia",
                        "detected_at": datetime.now().isoformat()
                    })

            print(f"✅ Found {len(files)} potential rejection files on Bupa portal")

        except Exception as e:
            print(f"⚠️ Error checking Bupa for rejections: {str(e)}")

        return files

    async def download_rejection_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """Download rejection file from Bupa"""
        try:
            href = file_info.get("href")
            filename = file_info.get("filename")

            if not href or not filename:
                return None

            # Construct full URL if relative
            if href.startswith("/"):
                base_url = self.page.url.split("/", 3)[0] + "//" + self.page.url.split("/", 3)[2]
                url = base_url + href
            else:
                url = href

            # Download file
            async with self.page.expect_download() as download_info:
                await self.page.goto(url)

            download = await download_info.value
            file_path = self.download_dir / filename

            await download.save_as(str(file_path))
            print(f"✅ Downloaded Bupa rejection file: {filename}")

            return file_path

        except Exception as e:
            print(f"❌ Failed to download Bupa rejection file: {str(e)}")
            return None


class GlobeMedRejectionMonitor(RejectionMonitor):
    """Rejection monitor for GlobeMed portal"""

    async def check_for_rejection_files(self) -> List[Dict[str, Any]]:
        """
        Check GlobeMed portal for rejection/response files
        """
        files = []

        try:
            # Navigate to claim status/reports
            status_link = await self.page.query_selector("text=Claim Status") or \
                         await self.page.query_selector("text=Reports") or \
                         await self.page.query_selector("text=Download Reports")

            if status_link:
                await status_link.click()
                await self.page.wait_for_load_state("networkidle")

            # Look for rejection/response indicators
            rejection_patterns = [
                "rejection",
                "denied",
                "response",
                "eob",
                "claim status",
                "download report"
            ]

            # Check for file inputs or download buttons
            download_elements = await self.page.query_selector_all(
                "button:has-text('Download'), button:has-text('Export'), a[href*='.xls'], a[href*='.csv']"
            )

            for element in download_elements:
                text = await element.text_content()

                if any(pattern in text.lower() for pattern in rejection_patterns):
                    files.append({
                        "filename": f"globemed_rejection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        "element": element,
                        "text": text,
                        "payer": "GlobeMed",
                        "detected_at": datetime.now().isoformat()
                    })

            print(f"✅ Found {len(files)} potential rejection files on GlobeMed portal")

        except Exception as e:
            print(f"⚠️ Error checking GlobeMed for rejections: {str(e)}")

        return files

    async def download_rejection_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """Download rejection file from GlobeMed"""
        try:
            element = file_info.get("element")
            filename = file_info.get("filename")

            if not element or not filename:
                return None

            # Set download directory and click element
            file_path = self.download_dir / filename

            async with self.page.expect_download() as download_info:
                await element.click()

            download = await download_info.value
            await download.save_as(str(file_path))

            print(f"✅ Downloaded GlobeMed rejection file: {filename}")
            return file_path

        except Exception as e:
            print(f"❌ Failed to download GlobeMed rejection file: {str(e)}")
            return None


class WaseelRejectionMonitor(RejectionMonitor):
    """Rejection monitor for Waseel/Tawuniya portal"""

    async def check_for_rejection_files(self) -> List[Dict[str, Any]]:
        """
        Check Waseel/NPHIES portal for claim response files

        Can use NPHIES API endpoints for more reliable monitoring
        """
        files = []

        try:
            # Try to access Waseel claim status portal
            claim_status_url = "https://jisr.waseel.com/claim-status"

            try:
                await self.page.goto(claim_status_url, wait_until="networkidle", timeout=30000)

                # Look for rejection/response indicators
                responses = await self.page.query_selector_all(
                    "button:has-text('Download'), button:has-text('Export'), a[href*='.json'], a[href*='.xml']"
                )

                for response_elem in responses:
                    text = await response_elem.text_content()

                    if "rejection" in text.lower() or "response" in text.lower():
                        files.append({
                            "filename": f"waseel_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            "element": response_elem,
                            "text": text,
                            "payer": "Waseel/Tawuniya",
                            "detected_at": datetime.now().isoformat()
                        })

            except Exception as e:
                print(f"⚠️ Could not access Waseel portal: {str(e)}")

            # Alternative: Check for NPHIES API notifications
            print(f"✅ Found {len(files)} potential rejection files on Waseel portal")

        except Exception as e:
            print(f"⚠️ Error checking Waseel for rejections: {str(e)}")

        return files

    async def download_rejection_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """Download rejection file from Waseel/NPHIES"""
        try:
            element = file_info.get("element")
            filename = file_info.get("filename")

            if not element or not filename:
                return None

            file_path = self.download_dir / filename

            async with self.page.expect_download() as download_info:
                await element.click()

            download = await download_info.value
            await download.save_as(str(file_path))

            print(f"✅ Downloaded Waseel rejection file: {filename}")
            return file_path

        except Exception as e:
            print(f"❌ Failed to download Waseel rejection file: {str(e)}")
            return None


class RejectionMonitoringService:
    """Service to manage rejection monitoring across all payers"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.monitors = {}
        self.monitoring_tasks = {}

    async def start_monitoring(
        self,
        payer: str,
        username: str,
        password: str,
        monitoring_duration: int = 3600  # 1 hour
    ) -> Dict[str, Any]:
        """
        Start monitoring a specific payer for rejections

        Args:
            payer: Payer name (bupa, globemed, waseel)
            username: Portal username
            password: Portal password
            monitoring_duration: How long to monitor (seconds)

        Returns:
            Monitoring status and results
        """
        from automation.portal_bots.bupa_bot import BupaPortalBot
        from automation.portal_bots.globemed_bot import GlobeMedPortalBot
        from automation.portal_bots.waseel_bot import WaseelPortalBot

        try:
            # Initialize appropriate bot
            if payer.lower() == "bupa":
                bot = BupaPortalBot(headless=self.headless)
                monitor_class = BupaRejectionMonitor
            elif payer.lower() == "globemed":
                bot = GlobeMedPortalBot(headless=self.headless)
                monitor_class = GlobeMedRejectionMonitor
            elif payer.lower() in ["waseel", "tawuniya"]:
                bot = WaseelPortalBot(headless=self.headless)
                monitor_class = WaseelRejectionMonitor
            else:
                return {"status": "error", "message": f"Unknown payer: {payer}"}

            # Start bot and login
            async with bot:
                login_success = await bot.login(username, password)
                if not login_success:
                    return {"status": "error", "message": f"Login failed for {payer}"}

                # Start monitoring
                monitor = monitor_class(bot.page)
                detected_files = await monitor.monitor_for_rejections(
                    timeout_seconds=monitoring_duration
                )

                return {
                    "status": "success",
                    "payer": payer,
                    "files_detected": len(detected_files),
                    "files": detected_files,
                    "monitored_until": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "status": "error",
                "payer": payer,
                "message": f"Monitoring failed: {str(e)}"
            }

    async def monitor_all_payers(
        self,
        credentials: Dict[str, Dict[str, str]],
        monitoring_duration: int = 3600
    ) -> Dict[str, Any]:
        """
        Monitor all payers simultaneously

        Args:
            credentials: Dict of payer -> {username, password}
            monitoring_duration: Monitoring duration in seconds

        Returns:
            Combined monitoring results
        """
        tasks = []

        for payer, creds in credentials.items():
            task = self.start_monitoring(
                payer=payer,
                username=creds.get("username"),
                password=creds.get("password"),
                monitoring_duration=monitoring_duration
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        total_files = sum(r.get("files_detected", 0) for r in results if r.get("status") == "success")

        return {
            "status": "completed",
            "total_files_detected": total_files,
            "payer_results": results,
            "completed_at": datetime.now().isoformat()
        }


# Utility functions
async def monitor_payer_rejections(
    payer: str,
    username: str,
    password: str,
    duration: int = 3600
) -> Dict[str, Any]:
    """Utility function to start monitoring a payer"""
    service = RejectionMonitoringService()
    return await service.start_monitoring(payer, username, password, duration)


async def monitor_all_payers_rejections(
    credentials: Dict[str, Dict[str, str]],
    duration: int = 3600
) -> Dict[str, Any]:
    """Utility function to monitor all payers"""
    service = RejectionMonitoringService()
    return await service.monitor_all_payers(credentials, duration)


if __name__ == "__main__":
    print("RejectionMonitor module initialized")
