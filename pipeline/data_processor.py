"""
Advanced Data Processor for NPHIES
Intelligent data transformation and enrichment
"""
from typing import Dict, List, Optional
from datetime import datetime
import re
from pathlib import Path
import csv
import json

from utils.logger import get_logger
from utils.validators import NPHIESValidator

logger = get_logger("data_processor")


class NPHIESDataProcessor:
    """Advanced data processing and transformation"""
    
    def __init__(self):
        self.validator = NPHIESValidator()
    
    def process_csv_to_eligibility_batch(self, csv_file: str) -> List[Dict]:
        """
        Convert CSV file to eligibility batch format
        
        CSV Format: member_id, payer_id, service_date, patient_name, gender, dob
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of eligibility request dictionaries
        """
        batch = []
        errors = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate required fields
                        member_id = row.get('member_id', '').strip()
                        payer_id = row.get('payer_id', '').strip()
                        
                        if not member_id or not payer_id:
                            errors.append(f"Row {row_num}: Missing required fields")
                            continue
                        
                        # Build eligibility request
                        eligibility_req = {
                            "member_id": member_id,
                            "payer_id": payer_id,
                            "service_date": row.get('service_date', datetime.now().strftime('%Y-%m-%d')).strip()
                        }
                        
                        # Add optional fields
                        if row.get('patient_name'):
                            eligibility_req["patient_name"] = row['patient_name'].strip()
                        if row.get('gender'):
                            eligibility_req["patient_gender"] = row['gender'].strip().lower()
                        if row.get('dob'):
                            eligibility_req["patient_dob"] = row['dob'].strip()
                        
                        batch.append(eligibility_req)
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            logger.info(f"Processed {len(batch)} eligibility requests from CSV")
            if errors:
                logger.warning(f"Encountered {len(errors)} errors while processing CSV")
                for error in errors[:10]:  # Log first 10 errors
                    logger.warning(error)
            
            return batch
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            raise
    
    def process_claims_from_json(self, json_file: str) -> List[Dict]:
        """
        Load claims from JSON file
        
        Args:
            json_file: Path to JSON file with claims
            
        Returns:
            List of claim dictionaries
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single claim and array of claims
            if isinstance(data, dict):
                claims = [data]
            else:
                claims = data
            
            logger.info(f"Loaded {len(claims)} claims from JSON")
            return claims
            
        except Exception as e:
            logger.error(f"Error loading claims from JSON: {str(e)}")
            raise
    
    def enrich_member_data(self, member_data: Dict, reference_data: Dict) -> Dict:
        """
        Enrich member data with additional information from reference data
        
        Args:
            member_data: Basic member information
            reference_data: Additional reference data (demographics, history, etc.)
            
        Returns:
            Enriched member data
        """
        enriched = member_data.copy()
        
        member_id = member_data.get('member_id')
        if member_id and member_id in reference_data:
            ref = reference_data[member_id]
            
            # Add demographic data
            enriched.update({
                'patient_name': ref.get('name', enriched.get('patient_name')),
                'patient_gender': ref.get('gender', enriched.get('patient_gender')),
                'patient_dob': ref.get('dob', enriched.get('patient_dob')),
                'contact_phone': ref.get('phone'),
                'nationality': ref.get('nationality'),
                'id_type': ref.get('id_type', 'national_id')
            })
        
        return enriched
    
    def validate_and_clean_batch(self, batch: List[Dict], batch_type: str) -> tuple:
        """
        Validate and clean batch data
        
        Args:
            batch: List of records to validate
            batch_type: Type of batch (eligibility, claims, authorization)
            
        Returns:
            Tuple of (valid_records, invalid_records)
        """
        valid = []
        invalid = []
        
        for record in batch:
            errors = []
            
            if batch_type == "eligibility":
                # Validate member ID
                member_id = record.get('member_id')
                if member_id:
                    is_valid, msg = self.validator.validate_member_id(member_id)
                    if not is_valid:
                        errors.append(f"Invalid member_id: {msg}")
                else:
                    errors.append("Missing member_id")
                
                # Validate payer ID
                payer_id = record.get('payer_id')
                if payer_id:
                    is_valid, msg = self.validator.validate_payer_id(payer_id)
                    if not is_valid:
                        errors.append(f"Invalid payer_id: {msg}")
                else:
                    errors.append("Missing payer_id")
                
                # Validate date
                service_date = record.get('service_date')
                if service_date:
                    is_valid, msg = self.validator.validate_date(service_date)
                    if not is_valid:
                        errors.append(f"Invalid service_date: {msg}")
            
            elif batch_type == "claims":
                # Validate claim data
                if 'services' not in record:
                    errors.append("Missing services")
                elif not isinstance(record['services'], list) or len(record['services']) == 0:
                    errors.append("Services must be non-empty list")
                
                if 'total_amount' not in record:
                    errors.append("Missing total_amount")
                elif not isinstance(record.get('total_amount'), (int, float)):
                    errors.append("total_amount must be numeric")
            
            # Add to appropriate list
            if errors:
                record['validation_errors'] = errors
                invalid.append(record)
            else:
                valid.append(record)
        
        logger.info(f"Validation complete: {len(valid)} valid, {len(invalid)} invalid")
        return valid, invalid
    
    def transform_claim_to_nphies_format(self, claim_data: Dict) -> Dict:
        """
        Transform internal claim format to NPHIES-compatible format
        
        Args:
            claim_data: Claim data in internal format
            
        Returns:
            NPHIES-compatible claim data
        """
        transformed = {
            "claim_type": claim_data.get('type', 'professional'),
            "patient_id": claim_data.get('patient_id') or claim_data.get('patientId'),
            "member_id": claim_data.get('member_id') or claim_data.get('memberId'),
            "payer_id": claim_data.get('payer_id') or claim_data.get('payerId'),
            "claim_date": claim_data.get('claim_date') or claim_data.get('date'),
            "services": [],
            "total_amount": 0.0
        }
        
        # Transform services
        services = claim_data.get('services') or claim_data.get('items', [])
        for service in services:
            transformed_service = {
                "code": service.get('code') or service.get('service_code'),
                "description": service.get('description') or service.get('name'),
                "quantity": service.get('quantity', 1),
                "unit_price": float(service.get('unit_price', 0) or service.get('price', 0)),
                "net_amount": float(service.get('net_amount', 0) or service.get('amount', 0))
            }
            
            # Calculate net_amount if not provided
            if transformed_service['net_amount'] == 0:
                transformed_service['net_amount'] = (
                    transformed_service['quantity'] * transformed_service['unit_price']
                )
            
            transformed['services'].append(transformed_service)
            transformed['total_amount'] += transformed_service['net_amount']
        
        return transformed
    
    def deduplicate_batch(self, batch: List[Dict], key_field: str) -> List[Dict]:
        """
        Remove duplicate records from batch based on key field
        
        Args:
            batch: List of records
            key_field: Field to use for deduplication
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []
        duplicates = 0
        
        for record in batch:
            key = record.get(key_field)
            if key and key not in seen:
                seen.add(key)
                unique.append(record)
            else:
                duplicates += 1
        
        if duplicates > 0:
            logger.info(f"Removed {duplicates} duplicate records")
        
        return unique
    
    def split_batch(self, batch: List[Dict], batch_size: int) -> List[List[Dict]]:
        """
        Split large batch into smaller batches
        
        Args:
            batch: Large batch to split
            batch_size: Size of each sub-batch
            
        Returns:
            List of sub-batches
        """
        batches = []
        for i in range(0, len(batch), batch_size):
            batches.append(batch[i:i + batch_size])
        
        logger.info(f"Split batch of {len(batch)} into {len(batches)} sub-batches")
        return batches
    
    def merge_results(self, result_files: List[str]) -> Dict:
        """
        Merge multiple result files into single dataset
        
        Args:
            result_files: List of result file paths
            
        Returns:
            Merged results dictionary
        """
        merged = {
            "merged_at": datetime.now().isoformat(),
            "source_files": result_files,
            "total_records": 0,
            "data": []
        }
        
        for file_path in result_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different file formats
                if isinstance(data, dict) and 'data' in data:
                    records = data['data']
                elif isinstance(data, list):
                    records = data
                else:
                    records = [data]
                
                merged['data'].extend(records)
                merged['total_records'] += len(records)
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
        
        logger.info(f"Merged {merged['total_records']} records from {len(result_files)} files")
        return merged
    
    def export_to_csv(self, data: List[Dict], output_file: str, fields: List[str] = None):
        """
        Export data to CSV file
        
        Args:
            data: List of dictionaries to export
            output_file: Output CSV file path
            fields: List of fields to include (None = all fields)
        """
        if not data:
            logger.warning("No data to export")
            return
        
        try:
            # Determine fields
            if not fields:
                fields = list(data[0].keys())
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Exported {len(data)} records to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def generate_summary_stats(self, results: List[Dict]) -> Dict:
        """
        Generate summary statistics from results
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Summary statistics
        """
        stats = {
            "total_records": len(results),
            "successful": sum(1 for r in results if r.get('success')),
            "failed": sum(1 for r in results if not r.get('success')),
            "success_rate": 0.0,
            "unique_payers": len(set(r.get('payer_id') for r in results if r.get('payer_id'))),
            "unique_patients": len(set(r.get('patient_id') for r in results if r.get('patient_id')))
        }
        
        if stats['total_records'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total_records']) * 100
        
        return stats
