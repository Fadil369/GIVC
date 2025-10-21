import os
import logging
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

# Suggested libs:
# - pysmb for direct SMB reads (pip install pysmb)
# - or mount share to local path and use watchdog for monitoring

logger = logging.getLogger("rcm.network_fetcher")

class NetworkDataFetcher:
    def __init__(self, payer_code: str, network_path: str, download_dir: str):
        self.payer_code = payer_code
        self.network_path = network_path
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def list_recent_files(self, days: int = 7) -> List[Path]:
        """List files in network_path modified in the last `days`. If using mounted path,
        os.walk can be used. If SMB, use pysmb list path API."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        matches = []
        # simple local-mounted path logic (replace with pysmb for direct UNC access)
        for root, _, files in os.walk(self.network_path):
            for f in files:
                full = Path(root) / f
                try:
                    mtime = datetime.utcfromtimestamp(full.stat().st_mtime)
                    if mtime >= cutoff:
                        matches.append(full)
                except Exception:
                    logger.exception("Stat failed for %s", full)
        return matches

    def download_file(self, src: Path) -> Path:
        """Copy file locally to download_dir and return local path."""
        dest = self.download_dir / f"{self.payer_code}_{src.name}"
        # perform antivirus/validation before processing in production
        with open(src, "rb") as r, open(dest, "wb") as w:
            w.write(r.read())
        logger.info("Downloaded %s -> %s", src, dest)
        return dest

    def fetch_recent(self, days: int = 7, download: bool = True) -> List[Path]:
        files = self.list_recent_files(days)
        logger.info("Found %d recent files for %s", len(files), self.payer_code)
        if download:
            return [self.download_file(p) for p in files]
        return files

# Example usage:
# fetcher = NetworkDataFetcher("BUPA", r"\\128.1.1.86\InmaRCMRejection\Bupa", "./downloads")
# recent = fetcher.fetch_recent(days=30)