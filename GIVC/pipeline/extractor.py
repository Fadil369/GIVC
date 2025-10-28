"""
Data Extraction Pipeline for NPHIES
Orchestrates data extraction workflows
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from services.eligibility import EligibilityService
from services.claims import ClaimsService
from services.communication import CommunicationService
from config.settings import settings
from utils.logger import get_logger
from utils.helpers import format_date

logger = get_logger("extractor")


class NPHIESDataExtractor:
    """Extract data from NPHIES platform"""
    
    def __init__(self):
        self.eligibility_service = EligibilityService()
        self.claims_service = ClaimsService()
        self.communication_service = CommunicationService()
        self.results = {
            "eligibility": [],
            "claims": [],
            "communications": [],
            "errors": []
        }
    
    def extract_eligibility_batch(
        self,
        members: List[Dict],
        output_file: str = None
    ) -> Dict:
        """
        Extract eligibility data for multiple members
        
        Args:
            members: List of member dictionaries with required fields
            output_file: Optional file to save results
            
        Returns:
            Dictionary with extraction results
        """
        logger.info(f"Starting eligibility extraction for {len(members)} members")
        
        start_time = datetime.now()
        results = {
            "total": len(members),
            "successful": 0,
            "failed": 0,
            "data": []
        }
        
        try:
            for idx, member in enumerate(members, 1):
                logger.info(f"Processing member {idx}/{len(members)}")
                
                try:
                    result = self.eligibility_service.check_eligibility(**member)
                    
                    if result.get("success"):
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        self.results["errors"].append({
                            "type": "eligibility",
                            "member": member.get("member_id"),
                            "error": result.get("error")
                        })
                    
                    results["data"].append(result)
                    self.results["eligibility"].append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing member {member.get('member_id')}: {str(e)}")
                    results["failed"] += 1
                    self.results["errors"].append({
                        "type": "eligibility",
                        "member": member.get("member_id"),
                        "error": str(e)
                    })
            
            # Save results if output file specified
            if output_file:
                self._save_results(results, output_file)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Eligibility extraction complete: "
                f"{results['successful']} successful, "
                f"{results['failed']} failed "
                f"(Duration: {duration:.2f}s)"
            )
            
            results["duration_seconds"] = duration
            return results
            
        except Exception as e:
            logger.error(f"Error in batch eligibility extraction: {str(e)}", exc_info=True)
            raise
    
    def extract_claims_batch(
        self,
        claims_data: List[Dict],
        output_file: str = None
    ) -> Dict:
        """
        Extract/submit multiple claims
        
        Args:
            claims_data: List of claim dictionaries
            output_file: Optional file to save results
            
        Returns:
            Dictionary with extraction results
        """
        logger.info(f"Starting claims extraction for {len(claims_data)} claims")
        
        start_time = datetime.now()
        results = {
            "total": len(claims_data),
            "successful": 0,
            "failed": 0,
            "data": []
        }
        
        try:
            for idx, claim in enumerate(claims_data, 1):
                logger.info(f"Processing claim {idx}/{len(claims_data)}")
                
                try:
                    result = self.claims_service.submit_claim(**claim)
                    
                    if result.get("success"):
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        self.results["errors"].append({
                            "type": "claim",
                            "claim_id": result.get("claim_id"),
                            "error": result.get("error")
                        })
                    
                    results["data"].append(result)
                    self.results["claims"].append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing claim: {str(e)}")
                    results["failed"] += 1
                    self.results["errors"].append({
                        "type": "claim",
                        "error": str(e)
                    })
            
            if output_file:
                self._save_results(results, output_file)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Claims extraction complete: "
                f"{results['successful']} successful, "
                f"{results['failed']} failed "
                f"(Duration: {duration:.2f}s)"
            )
            
            results["duration_seconds"] = duration
            return results
            
        except Exception as e:
            logger.error(f"Error in batch claims extraction: {str(e)}", exc_info=True)
            raise
    
    def poll_all_communications(self, output_file: str = None) -> Dict:
        """
        Poll for all pending communications
        
        Args:
            output_file: Optional file to save results
            
        Returns:
            Dictionary with poll results
        """
        logger.info("Polling for communications")
        
        try:
            result = self.communication_service.poll_communications()
            
            if result.get("success"):
                communications = result.get("communications", [])
                logger.info(f"Retrieved {len(communications)} communications")
                
                self.results["communications"].extend(communications)
                
                if output_file:
                    self._save_results(result, output_file)
            else:
                logger.warning(f"Communication poll failed: {result.get('errors')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error polling communications: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_full_extraction(
        self,
        eligibility_members: List[Dict] = None,
        claims_data: List[Dict] = None,
        poll_communications: bool = True,
        output_dir: str = "output"
    ) -> Dict:
        """
        Run full data extraction pipeline
        
        Args:
            eligibility_members: List of members for eligibility check
            claims_data: List of claims to submit
            poll_communications: Whether to poll communications
            output_dir: Directory to save results
            
        Returns:
            Dictionary with complete extraction results
        """
        logger.info("=== Starting full NPHIES data extraction ===")
        
        start_time = datetime.now()
        pipeline_results = {
            "start_time": start_time.isoformat(),
            "eligibility": None,
            "claims": None,
            "communications": None,
            "summary": {}
        }
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Extract eligibility data
        if eligibility_members:
            logger.info("--- Phase 1: Eligibility Extraction ---")
            pipeline_results["eligibility"] = self.extract_eligibility_batch(
                eligibility_members,
                output_file=str(output_path / "eligibility_results.json")
            )
        
        # Extract claims data
        if claims_data:
            logger.info("--- Phase 2: Claims Extraction ---")
            pipeline_results["claims"] = self.extract_claims_batch(
                claims_data,
                output_file=str(output_path / "claims_results.json")
            )
        
        # Poll communications
        if poll_communications:
            logger.info("--- Phase 3: Communications Polling ---")
            pipeline_results["communications"] = self.poll_all_communications(
                output_file=str(output_path / "communications_results.json")
            )
        
        # Calculate summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        pipeline_results["end_time"] = end_time.isoformat()
        pipeline_results["duration_seconds"] = duration
        pipeline_results["summary"] = {
            "total_eligibility": len(eligibility_members) if eligibility_members else 0,
            "total_claims": len(claims_data) if claims_data else 0,
            "total_communications": len(self.results["communications"]),
            "total_errors": len(self.results["errors"]),
            "duration": f"{duration:.2f}s"
        }
        
        # Save complete results
        complete_results_file = output_path / "complete_extraction_results.json"
        self._save_results(pipeline_results, str(complete_results_file))
        
        logger.info(f"=== Extraction complete in {duration:.2f}s ===")
        logger.info(f"Results saved to: {output_path}")
        
        return pipeline_results
    
    def _save_results(self, data: Dict, filename: str):
        """Save results to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {filename}")
        except Exception as e:
            logger.error(f"Error saving results to {filename}: {str(e)}")
    
    def get_all_results(self) -> Dict:
        """Get all accumulated results"""
        return self.results
