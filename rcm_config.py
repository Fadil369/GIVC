# Example multi-payer configuration (drop into config package)
from typing import Dict, Any

RCM_PAYERS: Dict[str, Dict[str, Any]] = {
    "BUPA": {
        "name": "Bupa Arabia",
        "code": "BUPA",
        "network_path": r"\\128.1.1.86\InmaRCMRejection\Bupa",
        "branches": ["Jizan", "Khamis", "Madinah", "Riyadh", "Unaizah"],
        "turnaround_days": 15,
        "appeal_deadline_days": 90,
        "adapter": "bupa_adapter",
    },
    "ALTAWUNIYA": {
        "name": "Al-Tawuniya Insurance",
        "code": "ALTAWUNIYA",
        "network_path": r"\\128.1.1.86\InmaRCMRejection\Al Rajhi Takaful",
        "branches": ["All"],
        "turnaround_days": 20,
        "appeal_deadline_days": 60,
        "adapter": "altawuniya_adapter",
    },
    "MOH": {
        "name": "Ministry of Health - GlobeMed",
        "code": "MOH",
        "network_path": r"\\128.1.1.86\InmaRCMRejection\MOH rejection",
        "branches": ["All"],
        "turnaround_days": 30,
        "appeal_deadline_days": 180,
        "adapter": "moh_adapter",
        "nphies": True,
    },
    # add more payers...
}