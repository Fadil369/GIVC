"""
Medical Billing Rejection Analysis Script

This script specifically analyzes medical billing rejections from MWS Statement of Account Excel files.
It identifies rejection patterns, analyzes reasons, and generates actionable reports and training materials.

Main functions:
- load_mws_excel_files() - Load MWS Statement of Account Excel files
- analyze_rejections() - Analyze rejection patterns
- generate_reports() - Generate summary reports
- prepare_training_materials() - Create doctor-specific training modules
"""

import os
import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict, Counter
import re
import logging
import matplotlib.pyplot as plt
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("medical_billing_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def load_mws_excel_files(file_path):
    """
    Load and parse MWS Statement of Account Excel files.
    
    Parameters:
    -----------
    file_path : str
        Path to the MWS Excel file.
        
    Returns:
    --------
    DataFrame: rejection_data
        DataFrame containing the processed rejection data.
    """
    try:
        logger.info(f"Loading MWS file from {file_path}")
        
        # Read all sheets to identify the main data sheet
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        logger.info(f"Found {len(sheet_names)} sheets: {sheet_names}")
        
        # Look for the main data sheet - typically it has many columns and is not named "Sheet1"
        main_sheet = None
        max_columns = 0
        
        for sheet in sheet_names:
            # Read first row to get column count
            df_sample = pd.read_excel(file_path, sheet_name=sheet, nrows=1)
            col_count = len(df_sample.columns)
            
            if col_count > max_columns:
                max_columns = col_count
                main_sheet = sheet
        
        if not main_sheet:
            main_sheet = sheet_names[0]  # Default to first sheet if no suitable sheet found
            
        logger.info(f"Selected main data sheet: {main_sheet} with {max_columns} columns")
        
        # Read the main data sheet
        rejection_data = pd.read_excel(file_path, sheet_name=main_sheet)
        
        # Clean column names - strip whitespace and ensure consistent naming
        rejection_data.columns = [str(col).strip().replace(' ', '_') for col in rejection_data.columns]
        
        # Drop rows where all fields are NaN
        rejection_data = rejection_data.dropna(how='all')
        
        # Fix data types
        if 'Rejected_Amount' in rejection_data.columns:
            rejection_data['Rejected_Amount'] = pd.to_numeric(rejection_data['Rejected_Amount'], errors='coerce')
        
        if 'Exceed_Price' in rejection_data.columns:
            rejection_data['Exceed_Price'] = pd.to_numeric(rejection_data['Exceed_Price'], errors='coerce')
        
        # Ensure all string columns are string type
        for col in rejection_data.columns:
            if rejection_data[col].dtype == 'object':
                rejection_data[col] = rejection_data[col].astype(str).replace('nan', '')
        
        logger.info(f"Successfully loaded data with {len(rejection_data)} records and {len(rejection_data.columns)} columns")
        
        # Print column names for reference
        logger.info(f"Columns in dataset: {rejection_data.columns.tolist()}")
        
        return rejection_data
        
    except Exception as e:
        logger.error(f"Error loading MWS file: {str(e)}")
        return pd.DataFrame()

def extract_diagnosis_codes(reason_text):
    """
    Extract diagnosis codes from rejection reason text.
    
    Parameters:
    -----------
    reason_text : str
        The rejection reason text.
        
    Returns:
    --------
    list: diagnosis_codes
        List of extracted diagnosis codes.
    """
    if not isinstance(reason_text, str) or pd.isna(reason_text) or reason_text == '':
        return []
    
    # Pattern for ICD-10 codes (letter followed by numbers and possibly decimal)
    pattern = r'([A-Z]\d+(?:\.\d+)?)'
    
    # Find all matches
    matches = re.findall(pattern, reason_text)
    
    return matches

def extract_medication_codes(reason_text):
    """
    Extract medication codes from rejection reason text.
    
    Parameters:
    -----------
    reason_text : str
        The rejection reason text.
        
    Returns:
    --------
    list: medication_codes
        List of extracted medication codes.
    """
    if not isinstance(reason_text, str) or pd.isna(reason_text) or reason_text == '':
        return []
    
    # Pattern for medication codes (looking for various formats found in the data)
    patterns = [
        r'Medication\s+([0-9A-Z\-]+)',  # Standard "Medication CODE" format
        r'requested drug\s*:\s*(\d+)',  # Format like "Requested drug : 2501233168"
        r'drug code\s*:\s*([A-Z0-9]+)', # "Drug code: ABC123" format
        r'NDC\s*:?\s*([0-9\-]+)',       # NDC code format
        r'([0-9]{4,})'                  # Any sequence of 4+ digits that might be a drug code
    ]
    
    # Find all matches across all patterns
    all_matches = []
    for pattern in patterns:
        matches = re.findall(pattern, reason_text, re.IGNORECASE)
        all_matches.extend(matches)
    
    # Filter out false positives (very short codes, etc.)
    filtered_matches = [match for match in all_matches if len(match) >= 4]
    
    return filtered_matches

def analyze_rejections(rejection_data):
    """
    Analyze rejection patterns in the dataset.
    
    Parameters:
    -----------
    rejection_data : DataFrame
        DataFrame with rejection records.
        
    Returns:
    --------
    dict: analysis_results
        Dictionary containing various analysis results.
    """
    if rejection_data.empty:
        logger.error("Cannot analyze empty DataFrame")
        return {}
    
    analysis_results = {}
    
    try:
        # Check for Reason column
        reason_col = None
        for col in rejection_data.columns:
            if 'reason' in col.lower():
                reason_col = col
                break
        
        if not reason_col:
            logger.warning("Could not find a 'Reason' column in the data")
            reason_col = 'Reason'  # Default name, may be empty
            
        # Provider/doctor column
        doctor_col = None
        for col in rejection_data.columns:
            if 'doctor' in col.lower() or 'provider' in col.lower():
                doctor_col = col
                break
        
        if not doctor_col:
            logger.warning("Could not find a doctor/provider column in the data")
            doctor_col = 'Doctor_Code'  # Default name based on sample data
        
        # Service column
        service_col = None
        for col in rejection_data.columns:
            if 'service' in col.lower() and 'id' not in col.lower() and 'code' not in col.lower():
                service_col = col
                break
        
        if not service_col:
            logger.warning("Could not find a service description column in the data")
            for col in rejection_data.columns:
                if 'service' in col.lower():
                    service_col = col
                    break
        
        # Service code column
        service_code_col = None
        for col in rejection_data.columns:
            if ('service' in col.lower() and 'code' in col.lower()) or 'cpt' in col.lower() or 'hcpcs' in col.lower():
                service_code_col = col
                break
        
        if not service_code_col:
            logger.warning("Could not find a service code column in the data")
            service_code_col = 'Service_Code'  # Default name based on sample data
        
        # Amount columns
        rejected_amount_col = None
        for col in rejection_data.columns:
            if 'reject' in col.lower() and ('amount' in col.lower() or 'price' in col.lower() or 'cost' in col.lower()):
                rejected_amount_col = col
                break
        
        if not rejected_amount_col:
            logger.warning("Could not find a rejected amount column in the data")
            rejected_amount_col = 'Rejected_Amount'  # Default name based on sample data
        
        # Process rejection reasons if the column exists
        if reason_col in rejection_data.columns:
            # Extract common rejection patterns
            rejection_data['rejection_category'] = rejection_data[reason_col].apply(categorize_rejection)
            
            # Extract diagnosis codes from rejection reasons
            rejection_data['diagnosis_codes'] = rejection_data[reason_col].apply(extract_diagnosis_codes)
            
            # Extract medication codes from rejection reasons
            rejection_data['medication_codes'] = rejection_data[reason_col].apply(extract_medication_codes)
            
            # Count rejection categories
            rejection_categories = rejection_data['rejection_category'].value_counts().reset_index()
            rejection_categories.columns = ['rejection_category', 'count']
            analysis_results['rejection_categories'] = rejection_categories.to_dict('records')
            
            # Top 5 rejection categories
            top_rejections = rejection_categories.head(5).to_dict('records')
            analysis_results['top_5_rejection_trends'] = top_rejections
        else:
            logger.warning(f"Reason column '{reason_col}' not found in data")
        
        # Doctor/provider analysis
        if doctor_col in rejection_data.columns:
            # Group by doctor and count rejections
            doctor_rejections = rejection_data.groupby(doctor_col).size().reset_index(name='rejection_count')
            doctor_rejections = doctor_rejections.sort_values('rejection_count', ascending=False)
            analysis_results['rejections_by_doctor'] = doctor_rejections.head(10).to_dict('records')
            
            # Doctors with rejection categories
            if 'rejection_category' in rejection_data.columns:
                doctor_categories = rejection_data.groupby([doctor_col, 'rejection_category']).size().reset_index(name='count')
                doctor_categories = doctor_categories.sort_values('count', ascending=False)
                analysis_results['doctor_rejection_categories'] = doctor_categories.head(20).to_dict('records')
        else:
            logger.warning(f"Doctor column '{doctor_col}' not found in data")
        
        # Service analysis
        if service_col in rejection_data.columns:
            # Common rejected services
            service_rejections = rejection_data.groupby(service_col).size().reset_index(name='rejection_count')
            service_rejections = service_rejections.sort_values('rejection_count', ascending=False)
            analysis_results['rejections_by_service'] = service_rejections.head(10).to_dict('records')
        else:
            logger.warning(f"Service column '{service_col}' not found in data")
        
        # Service code analysis
        if service_code_col in rejection_data.columns:
            # Common rejected service codes
            code_rejections = rejection_data.groupby(service_code_col).size().reset_index(name='rejection_count')
            code_rejections = code_rejections.sort_values('rejection_count', ascending=False)
            analysis_results['rejections_by_service_code'] = code_rejections.head(10).to_dict('records')
        else:
            logger.warning(f"Service code column '{service_code_col}' not found in data")
        
        # Financial impact analysis
        if rejected_amount_col in rejection_data.columns:
            # Convert to numeric if needed
            if not pd.api.types.is_numeric_dtype(rejection_data[rejected_amount_col]):
                rejection_data[rejected_amount_col] = pd.to_numeric(rejection_data[rejected_amount_col], errors='coerce')
            
            # Total rejected amount
            total_rejected = rejection_data[rejected_amount_col].sum()
            analysis_results['total_rejected_amount'] = float(total_rejected)
            
            # Rejected amount by doctor
            if doctor_col in rejection_data.columns:
                doctor_amounts = rejection_data.groupby(doctor_col)[rejected_amount_col].sum().reset_index()
                doctor_amounts = doctor_amounts.sort_values(rejected_amount_col, ascending=False)
                analysis_results['rejected_amounts_by_doctor'] = doctor_amounts.head(10).to_dict('records')
            
            # Rejected amount by service code
            if service_code_col in rejection_data.columns:
                code_amounts = rejection_data.groupby(service_code_col)[rejected_amount_col].sum().reset_index()
                code_amounts = code_amounts.sort_values(rejected_amount_col, ascending=False)
                analysis_results['rejected_amounts_by_service_code'] = code_amounts.head(10).to_dict('records')
        else:
            logger.warning(f"Rejected amount column '{rejected_amount_col}' not found in data")
        
        # Diagnosis code analysis
        if 'diagnosis_codes' in rejection_data.columns:
            # Extract all diagnosis codes
            all_codes = []
            for codes in rejection_data['diagnosis_codes']:
                all_codes.extend(codes)
            
            # Count diagnosis codes
            code_counts = Counter(all_codes)
            diagnosis_counts = pd.DataFrame({
                'diagnosis_code': list(code_counts.keys()),
                'count': list(code_counts.values())
            })
            diagnosis_counts = diagnosis_counts.sort_values('count', ascending=False)
            analysis_results['common_diagnosis_codes'] = diagnosis_counts.head(10).to_dict('records')
        
        # Medication code analysis
        if 'medication_codes' in rejection_data.columns:
            # Extract all medication codes
            all_meds = []
            for meds in rejection_data['medication_codes']:
                all_meds.extend(meds)
            
            # Count medication codes
            med_counts = Counter(all_meds)
            medication_counts = pd.DataFrame({
                'medication_code': list(med_counts.keys()),
                'count': list(med_counts.values())
            })
            medication_counts = medication_counts.sort_values('count', ascending=False)
            analysis_results['common_medication_codes'] = medication_counts.head(10).to_dict('records')
        
        logger.info("Completed rejection analysis")
        return analysis_results
        
    except Exception as e:
        logger.error(f"Error during rejection analysis: {str(e)}")
        return {}

def categorize_rejection(reason_text):
    """
    Categorize rejection reasons into standard categories.
    
    Parameters:
    -----------
    reason_text : str
        The rejection reason text.
        
    Returns:
    --------
    str: category
        The categorized rejection reason.
    """
    if not isinstance(reason_text, str) or pd.isna(reason_text) or reason_text == '':
        return "Unknown"
    
    reason_lower = reason_text.lower()
    
    # Define patterns and corresponding categories
    patterns = {
        'medication not indicated': ['medication', 'not indicated', 'diagnosis', 'requested drug'],
        'quantity limits exceeded': ['quantity exceeds', 'exceed policy', 'quantity limit', 'dosage exceed'],
        'missing documentation': ['missing', 'documentation', 'insufficient', 'incomplete'],
        'non-covered service': ['non-covered', 'not covered', 'excluded', 'non covered', 'non-preferred'],
        'coding error': ['coding', 'code', 'incorrect code'],
        'duplicate claim': ['duplicate', 'already submitted', 'already approved', 'duplicate request'],
        'authorization required': ['authorization', 'prior auth', 'pre-auth', 'not authorized'],
        'patient eligibility': ['eligibility', 'not eligible', 'coverage', 'not active'],
        'exceeds allowed amount': ['exceeds', 'allowed amount', 'price exceeds', 'exceed policy basic limit', 'cost exceed'],
        'medical necessity': ['medical necessity', 'not medically necessary', 'clinically appropriate'],
        'drug not on formulary': ['formulary', 'non-formulary', 'not on list', 'not in formulary'],
        'step therapy required': ['step therapy', 'first line', 'try alternative', 'preferred alternative'],
        'diagnosis restrictions': ['diagnosis restriction', 'not approved for diagnosis', 'indication']
    }
    
    # Check for matches
    for category, keywords in patterns.items():
        if any(keyword in reason_lower for keyword in keywords):
            return category
    
    return "Other"

def generate_resolution_suggestions(rejection_category):
    """
    Generate actionable suggestions based on rejection category.
    
    Parameters:
    -----------
    rejection_category : str
        The category of claim rejection.
        
    Returns:
    --------
    list: suggestions
        List of suggested actions to resolve the rejection.
    """
    # Map categories to resolution suggestions
    suggestion_map = {
        'medication not indicated': [
            'Review medication-diagnosis matching guidelines',
            'Ensure appropriate documentation of medical necessity',
            'Check diagnosis codes for accuracy and specificity',
            'Consider alternative medications with approved indications'
        ],
        'missing documentation': [
            'Implement documentation checklist for each service type',
            'Ensure all required elements are included in documentation',
            'Perform pre-submission review of documentation completeness',
            'Use electronic documentation templates with required fields'
        ],
        'non-covered service': [
            'Verify coverage before providing service',
            'Obtain Advance Beneficiary Notice when applicable',
            'Provide patients with clear information about non-covered services',
            'Consider alternative covered procedures'
        ],
        'coding error': [
            'Implement regular coding audit process',
            'Provide ongoing training on correct code usage',
            'Use coding verification software',
            'Consult current coding guidelines for proper coding'
        ],
        'duplicate claim': [
            'Implement claim tracking system',
            'Verify claim status before resubmission',
            'Use unique identifiers for all claims',
            'Document all claim submission activities'
        ],
        'authorization required': [
            'Verify authorization requirements before service',
            'Implement authorization tracking system',
            'Document authorization number on all claims',
            'Create process for checking authorization status'
        ],
        'patient eligibility': [
            'Verify insurance eligibility before service',
            'Implement real-time eligibility verification',
            'Update patient information at each visit',
            'Establish a pre-visit verification protocol'
        ],
        'exceeds allowed amount': [
            'Verify contracted rates before billing',
            'Update fee schedules regularly',
            'Review contract terms for maximum allowable charges',
            'Implement pricing compliance checks'
        ],
        'medical necessity': [
            'Document clinical indications clearly',
            'Reference evidence-based guidelines in documentation',
            'Ensure documentation supports medical necessity',
            'Implement peer review for complex cases'
        ],
        'other': [
            'Review payer guidelines for specific requirements',
            'Contact payer for clarification',
            'Verify all claim information for accuracy',
            'Consider appealing with additional documentation'
        ]
    }
    
    # Default suggestions if category not found
    default_suggestions = [
        'Review payer guidelines for specific requirements',
        'Contact payer for clarification',
        'Verify all claim information for accuracy',
        'Consider appealing with additional documentation'
    ]
    
    # Return suggestions for the category, or default if not found
    return suggestion_map.get(rejection_category.lower(), default_suggestions)

def generate_reports(analysis_results, output_dir=None, filename_prefix='claim_analysis'):
    """
    Generate Excel and TXT reports with analysis results.
    
    Parameters:
    -----------
    analysis_results : dict
        Dictionary containing various analysis results.
    output_dir : Path or str, optional
        Directory to save the reports.
    filename_prefix : str, optional
        Prefix for the output filenames.
        
    Returns:
    --------
    tuple: (excel_report_path, txt_report_path)
        Paths to the generated report files.
    """
    if not analysis_results:
        logger.error("Cannot generate reports from empty analysis results")
        return None, None
    
    if output_dir is None:
        output_dir = create_output_directory()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)
    
    # Add timestamp to filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_report_path = output_dir / f"{filename_prefix}_{timestamp}.xlsx"
    txt_report_path = output_dir / f"{filename_prefix}_{timestamp}.txt"
    
    # --- Generate Excel Report ---
    try:
        with pd.ExcelWriter(excel_report_path, engine='openpyxl') as writer:
            # Sheet 1: Executive Summary
            summary_data = []
            
            if 'total_rejected_amount' in analysis_results:
                summary_data.append({
                    'Metric': 'Total Rejected Amount',
                    'Value': f"${analysis_results['total_rejected_amount']:,.2f}"
                })
            
            if 'top_5_rejection_trends' in analysis_results:
                top_reason = analysis_results['top_5_rejection_trends'][0]['rejection_category'] if analysis_results['top_5_rejection_trends'] else 'None'
                summary_data.append({
                    'Metric': 'Top Rejection Reason',
                    'Value': top_reason
                })
            
            if 'rejections_by_doctor' in analysis_results:
                top_doctor = analysis_results['rejections_by_doctor'][0][list(analysis_results['rejections_by_doctor'][0].keys())[0]] if analysis_results['rejections_by_doctor'] else 'None'
                summary_data.append({
                    'Metric': 'Doctor with Most Rejections',
                    'Value': top_doctor
                })
            
            if 'rejections_by_service_code' in analysis_results:
                top_service = analysis_results['rejections_by_service_code'][0][list(analysis_results['rejections_by_service_code'][0].keys())[0]] if analysis_results['rejections_by_service_code'] else 'None'
                summary_data.append({
                    'Metric': 'Service Code with Most Rejections',
                    'Value': top_service
                })
            
            # Add total count of rejections
            if any('count' in item for item in analysis_results.get('rejection_categories', [])):
                total_rejections = sum(item['count'] for item in analysis_results['rejection_categories'])
                summary_data.append({
                    'Metric': 'Total Rejections Analyzed',
                    'Value': total_rejections
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sheet 2: Top Rejection Categories
            if 'rejection_categories' in analysis_results:
                rejection_categories_df = pd.DataFrame(analysis_results['rejection_categories'])
                rejection_categories_df.to_excel(
                    writer, sheet_name='Rejection Categories', index=False)
            
            # Sheet 3: Doctor Analysis
            if 'rejections_by_doctor' in analysis_results:
                rejections_by_doctor_df = pd.DataFrame(analysis_results['rejections_by_doctor'])
                rejections_by_doctor_df.to_excel(
                    writer, sheet_name='Doctor Analysis', index=False)
            
            # Sheet 4: Doctor Rejection Categories
            if 'doctor_rejection_categories' in analysis_results:
                doctor_rejection_categories_df = pd.DataFrame(analysis_results['doctor_rejection_categories'])
                doctor_rejection_categories_df.to_excel(
                    writer, sheet_name='Doctor Rejection Types', index=False)
            
            # Sheet 5: Service Analysis
            if 'rejections_by_service' in analysis_results:
                rejections_by_service_df = pd.DataFrame(analysis_results['rejections_by_service'])
                rejections_by_service_df.to_excel(
                    writer, sheet_name='Service Analysis', index=False)
            
            # Sheet 6: Service Code Analysis
            if 'rejections_by_service_code' in analysis_results:
                rejections_by_service_code_df = pd.DataFrame(analysis_results['rejections_by_service_code'])
                rejections_by_service_code_df.to_excel(
                    writer, sheet_name='Service Code Analysis', index=False)
            
            # Sheet 7: Financial Impact by Doctor
            if 'rejected_amounts_by_doctor' in analysis_results:
                rejected_amounts_by_doctor_df = pd.DataFrame(analysis_results['rejected_amounts_by_doctor'])
                rejected_amounts_by_doctor_df.to_excel(
                    writer, sheet_name='Financial Impact by Doctor', index=False)
            
            # Sheet 8: Financial Impact by Service
            if 'rejected_amounts_by_service_code' in analysis_results:
                rejected_amounts_by_service_code_df = pd.DataFrame(analysis_results['rejected_amounts_by_service_code'])
                rejected_amounts_by_service_code_df.to_excel(
                    writer, sheet_name='Financial Impact by Service', index=False)
            
            # Sheet 9: Diagnosis Code Analysis
            if 'common_diagnosis_codes' in analysis_results:
                common_diagnosis_codes_df = pd.DataFrame(analysis_results['common_diagnosis_codes'])
                common_diagnosis_codes_df.to_excel(
                    writer, sheet_name='Diagnosis Codes', index=False)
            
            # Sheet 10: Medication Code Analysis
            if 'common_medication_codes' in analysis_results:
                common_medication_codes_df = pd.DataFrame(analysis_results['common_medication_codes'])
                common_medication_codes_df.to_excel(
                    writer, sheet_name='Medication Codes', index=False)
            
            # Sheet 11: Resolution Suggestions
            if 'rejection_categories' in analysis_results:
                suggestions_data = []
                for item in analysis_results['rejection_categories']:
                    category = item['rejection_category']
                    suggestions = generate_resolution_suggestions(category)
                    suggestions_data.append({
                        'rejection_category': category,
                        'count': item['count'],
                        'resolution_suggestions': '; '.join(suggestions)
                    })
                suggestions_df = pd.DataFrame(suggestions_data)
                suggestions_df.to_excel(
                    writer, sheet_name='Resolution Suggestions', index=False)
        
        logger.info(f"Successfully generated Excel report at {excel_report_path}")
        
    except Exception as e:
        logger.error(f"Error generating Excel report: {str(e)}")
        excel_report_path = None # Ensure path is None if generation failed

    # --- Generate TXT Report ---
    try:
        with open(txt_report_path, 'w', encoding='utf-8') as f:
            f.write("Medical Billing Rejection Analysis Report\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*40 + "\n\n")

            # Write Executive Summary
            f.write("Executive Summary\n")
            f.write("-"*40 + "\n")
            if 'summary_df' in locals(): # Check if summary_df was created
                 f.write(summary_df.to_string(index=False, header=False))
                 f.write("\n\n")
            else:
                 f.write("Summary data not available.\n\n")

            # Write other sections
            report_sections = {
                "Rejection Categories": 'rejection_categories_df',
                "Doctor Analysis": 'rejections_by_doctor_df',
                "Doctor Rejection Types": 'doctor_rejection_categories_df',
                "Service Analysis": 'rejections_by_service_df',
                "Service Code Analysis": 'rejections_by_service_code_df',
                "Financial Impact by Doctor": 'rejected_amounts_by_doctor_df',
                "Financial Impact by Service": 'rejected_amounts_by_service_code_df',
                "Common Diagnosis Codes": 'common_diagnosis_codes_df',
                "Common Medication Codes": 'common_medication_codes_df',
                "Resolution Suggestions": 'suggestions_df'
            }

            for title, df_name in report_sections.items():
                f.write(f"{title}\n")
                f.write("-"*len(title) + "\n")
                if df_name in locals():
                    df_to_write = locals()[df_name]
                    # Format amount columns if they exist
                    for col in df_to_write.columns:
                         if 'amount' in col.lower() or 'price' in col.lower():
                              # Check if column is numeric before formatting
                              if pd.api.types.is_numeric_dtype(df_to_write[col]):
                                   df_to_write[col] = df_to_write[col].map('{:,.2f}'.format)
                    f.write(df_to_write.to_string(index=False))
                    f.write("\n\n")
                else:
                    f.write(f"{title} data not available.\n\n")

        logger.info(f"Successfully generated TXT report at {txt_report_path}")

    except Exception as e:
        logger.error(f"Error generating TXT report: {str(e)}")
        txt_report_path = None # Ensure path is None if generation failed

    # Generate charts (outside the try blocks for reports)
    try:
        generate_charts(analysis_results, output_dir, filename_prefix)
    except Exception as e:
        logger.error(f"Error during chart generation step: {str(e)}")

    return str(excel_report_path) if excel_report_path else None, str(txt_report_path) if txt_report_path else None

def generate_charts(analysis_results, output_dir, filename_prefix):
    """
    Generate charts based on analysis results.
    
    Parameters:
    -----------
    analysis_results : dict
        Dictionary containing various analysis results.
    output_dir : Path or str
        Directory to save the charts.
    filename_prefix : str
        Prefix for the output filenames.
    """
    try:
        # Ensure output directory exists
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        
        charts_dir = output_dir / 'charts'
        charts_dir.mkdir(exist_ok=True)
        
        # Chart 1: Rejection Categories Pie Chart
        if 'rejection_categories' in analysis_results:
            plt.figure(figsize=(10, 6))
            data = pd.DataFrame(analysis_results['rejection_categories']).head(5)
            
            plt.pie(data['count'], labels=data['rejection_category'], autopct='%1.1f%%', 
                   shadow=True, startangle=90)
            plt.axis('equal')
            plt.title('Top 5 Rejection Categories')
            plt.tight_layout()
            
            chart_path = charts_dir / f"{filename_prefix}_rejection_categories_pie.png"
            plt.savefig(chart_path)
            plt.close()
            logger.info(f"Generated pie chart at {chart_path}")
        
        # Chart 2: Top Doctors Bar Chart
        if 'rejections_by_doctor' in analysis_results:
            plt.figure(figsize=(12, 6))
            data = pd.DataFrame(analysis_results['rejections_by_doctor']).head(10)
            
            # Get the doctor column name (first column)
            doctor_col = data.columns[0]
            
            plt.barh(data[doctor_col], data['rejection_count'])
            plt.xlabel('Number of Rejections')
            plt.ylabel('Doctor')
            plt.title('Top 10 Doctors by Rejection Count')
            plt.tight_layout()
            
            chart_path = charts_dir / f"{filename_prefix}_doctors_bar.png"
            plt.savefig(chart_path)
            plt.close()
            logger.info(f"Generated doctor bar chart at {chart_path}")
        
        # Chart 3: Financial Impact by Service Code
        if 'rejected_amounts_by_service_code' in analysis_results:
            plt.figure(figsize=(12, 6))
            data = pd.DataFrame(analysis_results['rejected_amounts_by_service_code']).head(10)
            
            # Get the service code column name (first column)
            service_col = data.columns[0]
            # Get the amount column name (second column)
            amount_col = data.columns[1]
            
            plt.barh(data[service_col], data[amount_col])
            plt.xlabel('Rejected Amount ($)')
            plt.ylabel('Service Code')
            plt.title('Top 10 Service Codes by Rejected Amount')
            plt.tight_layout()
            
            chart_path = charts_dir / f"{filename_prefix}_financial_impact_bar.png"
            plt.savefig(chart_path)
            plt.close()
            logger.info(f"Generated financial impact chart at {chart_path}")
        
    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")

def prepare_training_materials(rejection_data, analysis_results, output_dir=None, min_rejections=3):
    """
    Generate personalized training materials for doctors with recurring rejections.
    
    Parameters:
    -----------
    rejection_data : DataFrame
        DataFrame with rejection records.
    analysis_results : dict
        Dictionary containing various analysis results.
    output_dir : Path or str, optional
        Directory to save the training materials.
    min_rejections : int
        Minimum number of rejections in a category to generate training.
        
    Returns:
    --------
    str: training_path
        Path to the generated training materials file.
    """
    if rejection_data.empty or not analysis_results:
        logger.error("Cannot prepare training materials from empty data")
        return None
    
    if output_dir is None:
        output_dir = create_output_directory()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    training_path = output_dir / f"doctor_training_modules_{timestamp}.json"
    
    try:
        # Find doctor column
        doctor_col = None
        for col in rejection_data.columns:
            if 'doctor' in col.lower() or 'provider' in col.lower():
                doctor_col = col
                break
        
        if not doctor_col:
            logger.error("Could not find doctor/provider column for training materials")
            return None
        
        # Find service column
        service_col = None
        for col in rejection_data.columns:
            if 'service' in col.lower() and 'id' not in col.lower() and 'code' not in col.lower():
                service_col = col
                break
        
        # Find payer column
        payer_col = None
        for col in rejection_data.columns:
            if 'payer' in col.lower() or 'insurer' in col.lower() or 'insurance' in col.lower():
                payer_col = col
                break
        
        # Process rejection categories if available
        if 'rejection_category' in rejection_data.columns and doctor_col in rejection_data.columns:
            # Group by doctor and rejection category to identify recurring issues
            doctor_issues = rejection_data.groupby([doctor_col, 'rejection_category']).size().reset_index(name='count')
            
            # Filter to include only significant issues
            doctor_issues = doctor_issues[doctor_issues['count'] >= min_rejections]
            
            # Sort by doctor and count
            doctor_issues = doctor_issues.sort_values([doctor_col, 'count'], ascending=[True, False])
            
            # Dictionary to store training modules by doctor
            training_modules = {}
            
            # Process each doctor's issues
            for doctor, group in doctor_issues.groupby(doctor_col):
                if not isinstance(doctor, str) or pd.isna(doctor) or doctor == '':
                    continue  # Skip doctors with invalid names
                
                doctor_data = rejection_data[rejection_data[doctor_col] == doctor].copy()
                
                # Skip if no meaningful data
                if len(doctor_data) < min_rejections:
                    continue
                
                # Find top rejection category for this doctor
                top_rejection = group.iloc[0]['rejection_category']
                rejection_count = group.iloc[0]['count']
                
                # Create a module for this doctor
                module = {
                    'doctor_name': doctor,
                    'total_rejections': len(doctor_data),
                    'top_rejection_category': top_rejection,
                    'rejection_count': int(rejection_count),
                    'common_issues': [],
                    'training_materials': [],
                    'affected_services': [],
                    'payer_recommendations': []
                }
                
                # Find services affected
                if service_col and service_col in doctor_data.columns:
                    affected_services = doctor_data.groupby([service_col, 'rejection_category']).size().reset_index(name='count')
                    affected_services = affected_services[affected_services['rejection_category'] == top_rejection]
                    affected_services = affected_services.sort_values('count', ascending=False)
                    
                    if not affected_services.empty:
                        module['affected_services'] = affected_services[[service_col, 'count']].head(5).to_dict('records')
                
                # Extract medications affected
                medications_affected = []
                if 'medication_codes' in doctor_data.columns:
                    for codes in doctor_data['medication_codes']:
                        medications_affected.extend(codes)
                medications_affected = list(set(medications_affected))
                
                # Get payer information
                payer = None
                if payer_col and payer_col in doctor_data.columns:
                    payers = doctor_data[payer_col].dropna().unique().tolist()
                    payer = payers[0] if payers else None
                
                # Get common issues description
                common_issues = []
                if 'diagnosis_codes' in doctor_data.columns:
                    diagnosis_codes = []
                    for codes in doctor_data['diagnosis_codes']:
                        diagnosis_codes.extend(codes)
                    
                    if diagnosis_codes:
                        common_issues.append(f"Issues with diagnosis codes: {', '.join(set(diagnosis_codes))}")
                
                if 'medication_codes' in doctor_data.columns and medications_affected:
                    common_issues.append(f"Medication indication issues with codes: {', '.join(medications_affected)}")
                
                # Default issue if none detected
                if not common_issues:
                    common_issues = ["Documentation and coding issues"]
                
                # Generate training materials
                training_materials = generate_resolution_suggestions(top_rejection)
                
                # Add payer-specific training if available
                if payer:
                    payer_recommendations = [
                        f"Review {payer}'s specific documentation requirements for {top_rejection.lower()} issues",
                        f"Contact {payer} provider representative for clarification on {top_rejection.lower()} policies"
                    ]
                    module['payer_recommendations'] = payer_recommendations
                
                # Add details to module
                module['common_issues'] = common_issues
                module['training_materials'] = training_materials
                
                # Add this doctor's module to the collection
                training_modules[doctor] = module
            
            # Save training modules to JSON file
            with open(training_path, 'w', encoding='utf-8') as f:
                json.dump(training_modules, f, indent=2)
            
            logger.info(f"Generated training materials for {len(training_modules)} doctors at {training_path}")
            
            # Also create a formatted text report for easier reading
            text_path = output_dir / f"doctor_training_modules_{timestamp}.txt"
            try:
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write("DOCTOR-SPECIFIC TRAINING MODULES\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for doctor, module in training_modules.items():
                        f.write(f"Doctor: {doctor}\n")
                        f.write("-" * 50 + "\n")
                        f.write(f"Total Rejections: {module['total_rejections']}\n")
                        f.write(f"Top Rejection Category: {module['top_rejection_category']} ({module['rejection_count']} occurrences)\n\n")
                        
                        f.write("Common Issues:\n")
                        for issue in module['common_issues']:
                            f.write(f"  - {issue}\n")
                        f.write("\n")
                        
                        f.write("Recommended Training:\n")
                        for item in module['training_materials']:
                            f.write(f"  - {item}\n")
                        f.write("\n")
                        
                        if module['affected_services']:
                            f.write("Most Affected Services:\n")
                            for service in module['affected_services']:
                                f.write(f"  - {service[service_col]} ({service['count']} rejections)\n")
                            f.write("\n")
                        
                        if 'payer_recommendations' in module and module['payer_recommendations']:
                            f.write("Payer-Specific Recommendations:\n")
                            for rec in module['payer_recommendations']:
                                f.write(f"  - {rec}\n")
                            f.write("\n")
                        
                        f.write("=" * 80 + "\n\n")
                
                logger.info(f"Generated formatted training text report at {text_path}")
                
            except Exception as e:
                logger.error(f"Error creating formatted training text report: {str(e)}")
            
            return str(training_path)
        else:
            logger.warning("Required columns for training materials not found")
            return None
            
    except Exception as e:
        logger.error(f"Error preparing training materials: {str(e)}")
        return None

def generate_advanced_insights(analysis_results, output_dir=None):
    """
    Generate advanced insights and recommendations based on rejection analysis.
    
    Parameters:
    -----------
    analysis_results : dict
        Dictionary containing various analysis results.
    output_dir : Path or str, optional
        Directory to save the insights reports.
        
    Returns:
    --------
    str: insight_report_path
        Path to the generated insights report file.
    """
    if not analysis_results:
        logger.error("Cannot generate insights from empty analysis results")
        return None
    
    if output_dir is None:
        output_dir = create_output_directory()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    insight_report_path = output_dir / f"insights_and_recommendations_{timestamp}.xlsx"
    
    try:
        # Calculate key metrics and trends
        insights = {}
        
        # Financial insights
        if 'total_rejected_amount' in analysis_results:
            total_rejected = analysis_results['total_rejected_amount']
            insights['financial_impact'] = {
                'total_rejected_amount': total_rejected,
                'severity': 'High' if total_rejected > 10000 else ('Medium' if total_rejected > 5000 else 'Low'),
                'recommendation': 'Implement weekly financial impact reviews for all rejections' if total_rejected > 10000 else 
                                 ('Establish monthly financial review process' if total_rejected > 5000 else 
                                  'Monitor financial trends quarterly')
            }
        
        # Top rejection trends
        if 'rejection_categories' in analysis_results:
            rejection_categories = pd.DataFrame(analysis_results['rejection_categories'])
            total_rejections = rejection_categories['count'].sum() if 'count' in rejection_categories.columns else 0
            
            if not rejection_categories.empty and 'count' in rejection_categories.columns and 'rejection_category' in rejection_categories.columns:
                # Calculate percentage of each category
                rejection_categories['percentage'] = (rejection_categories['count'] / total_rejections) * 100
                
                # Find categories that make up 80% of rejections (Pareto principle)
                rejection_categories = rejection_categories.sort_values('count', ascending=False)
                cumulative_pct = 0
                pareto_categories = []
                
                for _, row in rejection_categories.iterrows():
                    category = row['rejection_category']
                    count = row['count']
                    percentage = row['percentage']
                    cumulative_pct += percentage
                    pareto_categories.append({
                        'category': category,
                        'count': int(count),
                        'percentage': float(percentage),
                        'cumulative_percentage': float(cumulative_pct)
                    })
                    if cumulative_pct >= 80:
                        break
                
                insights['pareto_analysis'] = {
                    'principle': '80/20 Rule - Focus on these categories for highest impact',
                    'key_categories': pareto_categories,
                    'recommendation': 'Prioritize training and process improvement for these categories'
                }
        
        # Provider/Doctor insights
        if 'rejections_by_doctor' in analysis_results:
            doctor_rejections = pd.DataFrame(analysis_results['rejections_by_doctor'])
            
            if not doctor_rejections.empty:
                # Get the doctor column name (first column)
                doctor_col = doctor_rejections.columns[0]
                count_col = 'rejection_count'
                
                # Calculate statistics
                total_doctors = len(doctor_rejections)
                mean_rejections = doctor_rejections[count_col].mean()
                median_rejections = doctor_rejections[count_col].median()
                std_dev = doctor_rejections[count_col].std()
                
                # Identify outliers (doctors with rejection counts > 2 standard deviations from the mean)
                outlier_threshold = mean_rejections + (2 * std_dev)
                outliers = doctor_rejections[doctor_rejections[count_col] > outlier_threshold]
                
                insights['doctor_analysis'] = {
                    'total_doctors': int(total_doctors),
                    'average_rejections_per_doctor': float(mean_rejections),
                    'median_rejections': float(median_rejections),
                    'standard_deviation': float(std_dev),
                    'outlier_doctors': outliers[[doctor_col, count_col]].to_dict('records'),
                    'recommendation': 'Implement personalized coaching for outlier doctors'
                }
        
        # Service code insights
        if 'rejections_by_service_code' in analysis_results:
            service_rejections = pd.DataFrame(analysis_results['rejections_by_service_code'])
            
            if not service_rejections.empty:
                # Get the service code column name (first column)
                service_col = service_rejections.columns[0]
                count_col = 'rejection_count'
                
                # Identify high-frequency rejection services
                high_rejection_services = service_rejections.head(5)
                
                insights['service_analysis'] = {
                    'high_rejection_services': high_rejection_services[[service_col, count_col]].to_dict('records'),
                    'recommendation': 'Create service-specific documentation templates for high-rejection services'
                }
        
        # Trending analysis
        if 'rejection_categories' in analysis_results:
            top_trends = analysis_results['rejection_categories'][:3] if len(analysis_results['rejection_categories']) >= 3 else analysis_results['rejection_categories']
            
            trend_insights = []
            for trend in top_trends:
                category = trend['rejection_category']
                recommendations = generate_resolution_suggestions(category)
                
                trend_insights.append({
                    'category': category,
                    'count': trend['count'],
                    'key_actions': recommendations[:3],  # Top 3 recommendations
                    'priority': 'High'
                })
            
            insights['trending_recommendations'] = {
                'trends': trend_insights,
                'action_plan': 'Implement a 90-day improvement cycle focused on these top rejection reasons'
            }
        
        # Create Excel report with insights
        with pd.ExcelWriter(insight_report_path, engine='openpyxl') as writer:
            # Executive Summary Sheet
            summary_data = {
                'Insight Area': [],
                'Key Finding': [],
                'Priority': [],
                'Recommended Action': []
            }
            
            # Financial insights
            if 'financial_impact' in insights:
                fi = insights['financial_impact']
                summary_data['Insight Area'].append('Financial Impact')
                summary_data['Key Finding'].append(f"${fi['total_rejected_amount']:,.2f} in rejected claims")
                summary_data['Priority'].append(fi['severity'])
                summary_data['Recommended Action'].append(fi['recommendation'])
            
            # Pareto analysis
            if 'pareto_analysis' in insights:
                pa = insights['pareto_analysis']
                categories = ", ".join([item['category'] for item in pa['key_categories'][:3]])
                summary_data['Insight Area'].append('Rejection Categories')
                summary_data['Key Finding'].append(f"Top issues: {categories}")
                summary_data['Priority'].append('High')
                summary_data['Recommended Action'].append(pa['recommendation'])
            
            # Doctor analysis
            if 'doctor_analysis' in insights:
                da = insights['doctor_analysis']
                outlier_count = len(da['outlier_doctors'])
                summary_data['Insight Area'].append('Provider Performance')
                summary_data['Key Finding'].append(f"{outlier_count} providers with rejection rates > 2σ above mean")
                summary_data['Priority'].append('High' if outlier_count > 3 else 'Medium')
                summary_data['Recommended Action'].append(da['recommendation'])
            
            # Service analysis
            if 'service_analysis' in insights:
                sa = insights['service_analysis']
                if sa['high_rejection_services']:
                    top_service = sa['high_rejection_services'][0]
                    service_name = list(top_service.items())[0][1]  # Get first value from first item
                    summary_data['Insight Area'].append('Service Analysis')
                    summary_data['Key Finding'].append(f"High rejection rate for service: {service_name}")
                    summary_data['Priority'].append('Medium')
                    summary_data['Recommended Action'].append(sa['recommendation'])
            
            # Trending recommendations
            if 'trending_recommendations' in insights:
                tr = insights['trending_recommendations']
                if tr['trends']:
                    top_trend = tr['trends'][0]
                    summary_data['Insight Area'].append('Action Planning')
                    summary_data['Key Finding'].append(f"Focus on {top_trend['category']}")
                    summary_data['Priority'].append(top_trend['priority'])
                    summary_data['Recommended Action'].append(tr['action_plan'])
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive Insights', index=False)
            
            # Detailed Insights Sheets
            if 'pareto_analysis' in insights:
                pareto_df = pd.DataFrame(insights['pareto_analysis']['key_categories'])
                pareto_df.to_excel(writer, sheet_name='Pareto Analysis', index=False)
            
            if 'doctor_analysis' in insights:
                da = insights['doctor_analysis']
                
                # Summary stats
                stats_df = pd.DataFrame({
                    'Metric': ['Total Doctors', 'Average Rejections', 'Median Rejections', 'Standard Deviation'],
                    'Value': [da['total_doctors'], round(da['average_rejections_per_doctor'], 2), 
                              round(da['median_rejections'], 2), round(da['standard_deviation'], 2)]
                })
                stats_df.to_excel(writer, sheet_name='Doctor Analysis', index=False)
                
                # Outliers
                if da['outlier_doctors']:
                    outliers_df = pd.DataFrame(da['outlier_doctors'])
                    outliers_df.to_excel(writer, sheet_name='Doctor Analysis', index=False, startrow=len(stats_df) + 2)
            
            # Trending Actions Sheet
            if 'trending_recommendations' in insights:
                trends = insights['trending_recommendations']['trends']
                
                trend_data = {
                    'Category': [],
                    'Count': [],
                    'Priority': [],
                    'Action 1': [],
                    'Action 2': [],
                    'Action 3': []
                }
                
                for trend in trends:
                    trend_data['Category'].append(trend['category'])
                    trend_data['Count'].append(trend['count'])
                    trend_data['Priority'].append(trend['priority'])
                    
                    actions = trend['key_actions']
                    trend_data['Action 1'].append(actions[0] if len(actions) > 0 else '')
                    trend_data['Action 2'].append(actions[1] if len(actions) > 1 else '')
                    trend_data['Action 3'].append(actions[2] if len(actions) > 2 else '')
                
                trends_df = pd.DataFrame(trend_data)
                trends_df.to_excel(writer, sheet_name='Action Plan', index=False)
            
            # 90-Day Improvement Plan
            plan_data = {
                'Timeline': ['Days 1-30', 'Days 31-60', 'Days 61-90'],
                'Focus Area': ['Analysis & Training', 'Process Improvement', 'Monitoring & Refinement'],
                'Action Items': [
                    '1. Train staff on top rejection reasons\n2. Review documentation templates\n3. Implement quick wins',
                    '1. Deploy new documentation tools\n2. Establish payer-specific protocols\n3. Begin provider coaching',
                    '1. Measure improvement metrics\n2. Refine processes based on feedback\n3. Develop long-term strategy'
                ]
            }
            plan_df = pd.DataFrame(plan_data)
            plan_df.to_excel(writer, sheet_name='90-Day Plan', index=False)
        
        logger.info(f"Advanced insights report generated at {insight_report_path}")
        return str(insight_report_path)
    
    except Exception as e:
        logger.error(f"Error generating advanced insights: {str(e)}")
        return None

def generate_advanced_visualizations(analysis_results, output_dir, filename_prefix):
    """
    Generate advanced visualizations and dashboards based on analysis results.
    
    Parameters:
    -----------
    analysis_results : dict
        Dictionary containing various analysis results.
    output_dir : Path or str
        Directory to save the visualizations.
    filename_prefix : str
        Prefix for the output filenames.
    """
    try:
        # Ensure output directory exists
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        
        charts_dir = output_dir / 'charts'
        charts_dir.mkdir(exist_ok=True)
        
        # Set a more professional style for charts
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Chart 1: Enhanced Pareto Chart of Rejection Categories
        if 'rejection_categories' in analysis_results:
            plt.figure(figsize=(12, 7))
            data = pd.DataFrame(analysis_results['rejection_categories']).head(10)
            
            # Sort by count in descending order
            data = data.sort_values('count', ascending=False)
            
            # Calculate cumulative percentage
            total = data['count'].sum()
            data['cumulative_percentage'] = data['count'].cumsum() / total * 100
            
            # Create the bar chart
            ax1 = plt.subplot()
            bar_positions = np.arange(len(data))
            bars = ax1.bar(bar_positions, data['count'], color='steelblue', alpha=0.8)
            
            # Configure primary y-axis (left)
            ax1.set_ylabel('Number of Rejections', fontsize=12)
            ax1.set_ylim(0, data['count'].max() * 1.1)
            
            # Create secondary y-axis for percentage
            ax2 = ax1.twinx()
            ax2.plot(bar_positions, data['cumulative_percentage'], 'ro-', linewidth=2, markersize=6)
            ax2.set_ylabel('Cumulative Percentage', fontsize=12)
            ax2.set_ylim(0, 105)
            
            # Draw reference line for 80%
            ax2.axhline(y=80, linestyle='--', color='red', alpha=0.5)
            
            # Set the x-axis labels
            shortened_labels = [label[:20] + '...' if len(label) > 20 else label 
                               for label in data['rejection_category']]
            ax1.set_xticks(bar_positions)
            ax1.set_xticklabels(shortened_labels, rotation=45, ha='right')
            
            plt.title('Pareto Analysis of Rejection Categories', fontsize=14)
            plt.tight_layout()
            
            chart_path = charts_dir / f"{filename_prefix}_pareto_analysis.png"
            plt.savefig(chart_path, dpi=300)
            plt.close()
            logger.info(f"Generated Pareto chart at {chart_path}")
        
        # Chart 2: Financial Impact Heatmap by Service and Doctor
        if ('rejected_amounts_by_doctor' in analysis_results and 
            'rejected_amounts_by_service_code' in analysis_results):
            
            doctor_data = pd.DataFrame(analysis_results['rejected_amounts_by_doctor']).head(8)
            service_data = pd.DataFrame(analysis_results['rejected_amounts_by_service_code']).head(8)
            
            # Get column names
            doctor_col = doctor_data.columns[0]
            service_col = service_data.columns[0]
            amount_col = doctor_data.columns[1] if len(doctor_data.columns) > 1 else 'amount'
            
            # Create synthetic heatmap data - this would be better with real cross-tabulation data
            # In a real scenario, you'd create a proper cross-tab from the original data
            
            # Create a figure with 2 subplots side by side
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
            
            # Doctor rejections bar chart
            doctor_data = doctor_data.sort_values(amount_col)
            doctor_data.plot(kind='barh', x=doctor_col, y=amount_col, ax=ax1, 
                             color='cornflowerblue', legend=False)
            ax1.set_title('Rejection Amount by Doctor', fontsize=14)
            ax1.set_xlabel('Rejected Amount ($)', fontsize=12)
            
            # Add data labels to the bars
            for i, v in enumerate(doctor_data[amount_col]):
                ax1.text(v + 0.1, i, f'${v:,.2f}', va='center')
            
            # Service code rejections bar chart
            service_data = service_data.sort_values(amount_col)
            service_data.plot(kind='barh', x=service_col, y=amount_col, ax=ax2, 
                              color='indianred', legend=False)
            ax2.set_title('Rejection Amount by Service Code', fontsize=14)
            ax2.set_xlabel('Rejected Amount ($)', fontsize=12)
            
            # Add data labels to the bars
            for i, v in enumerate(service_data[amount_col]):
                ax2.text(v + 0.1, i, f'${v:,.2f}', va='center')
            
            plt.tight_layout()
            
            chart_path = charts_dir / f"{filename_prefix}_financial_impact_dashboard.png"
            plt.savefig(chart_path, dpi=300)
            plt.close()
            logger.info(f"Generated financial impact dashboard at {chart_path}")
        
        # Chart 3: Rejection Category Distribution Pie Chart with Exploded Slices
        if 'rejection_categories' in analysis_results:
            plt.figure(figsize=(10, 8))
            data = pd.DataFrame(analysis_results['rejection_categories']).head(6)
            
            # Prepare data
            labels = data['rejection_category']
            sizes = data['count']
              # Calculate percentages for labels
            total = sizes.sum()
            percentages = [100 * s / total for s in sizes]
            labels = [f'{label} ({pct:.1f}%)' for label, pct in zip(labels, percentages)]
            
            # Set colors and explosion
            colors = plt.cm.Paired(np.linspace(0, 1, len(sizes)))
            explode = [0.1 if i == 0 else 0.05 if i == 1 else 0 for i in range(len(sizes))]
            
            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='', shadow=True, startangle=90, 
                   wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Distribution of Rejection Categories', fontsize=16, pad=20)
            
            # Add a legend with percentages
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)
            
            plt.tight_layout()
            
            chart_path = charts_dir / f"{filename_prefix}_rejection_distribution_pie.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"Generated enhanced pie chart at {chart_path}")
        
        # Chart 4: Combined Dashboard
        plt.figure(figsize=(16, 12))
        
        # Create a 2x2 subplot layout
        gs = plt.GridSpec(2, 2, height_ratios=[1, 1])
        
        # Top left: Rejection Categories
        if 'rejection_categories' in analysis_results:
            ax1 = plt.subplot(gs[0, 0])
            data = pd.DataFrame(analysis_results['rejection_categories']).head(5)
            
            bars = ax1.bar(data['rejection_category'], data['count'], color='steelblue')
            ax1.set_title('Top Rejection Categories', fontsize=12)
            ax1.set_ylabel('Count', fontsize=10)
            plt.setp(ax1.get_xticklabels(), rotation=30, ha='right')
            
            # Add data labels
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=9)
        
        # Top right: Doctor Analysis
        if 'rejections_by_doctor' in analysis_results:
            ax2 = plt.subplot(gs[0, 1])
            data = pd.DataFrame(analysis_results['rejections_by_doctor']).head(5)
            
            # Get the doctor column name (first column)
            doctor_col = data.columns[0]
            
            bars = ax2.barh(data[doctor_col], data['rejection_count'], color='indianred')
            ax2.set_title('Top Doctors by Rejection Count', fontsize=12)
            ax2.set_xlabel('Number of Rejections', fontsize=10)
            
            # Add data labels
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                        f'{width:.0f}', ha='left', va='center', fontsize=9)
        
        # Bottom left: Service Analysis
        if 'rejections_by_service' in analysis_results:
            ax3 = plt.subplot(gs[1, 0])
            data = pd.DataFrame(analysis_results['rejections_by_service']).head(5)
            
            # Get the service column name (first column)
            service_col = data.columns[0]
            
            bars = ax3.bar(data[service_col], data['rejection_count'], color='forestgreen')
            ax3.set_title('Top Rejected Services', fontsize=12)
            ax3.set_ylabel('Count', fontsize=10)
            plt.setp(ax3.get_xticklabels(), rotation=30, ha='right')
            
            # Add data labels
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=9)
        
        # Bottom right: Financial Impact
        if 'rejected_amounts_by_service_code' in analysis_results:
            ax4 = plt.subplot(gs[1, 1])
            data = pd.DataFrame(analysis_results['rejected_amounts_by_service_code']).head(5)
            
            # Get the service code column name (first column)
            service_col = data.columns[0]
            # Get the amount column name (second column)
            amount_col = data.columns[1]
            
            bars = ax4.barh(data[service_col], data[amount_col], color='darkorange')
            ax4.set_title('Financial Impact by Service Code', fontsize=12)
            ax4.set_xlabel('Rejected Amount ($)', fontsize=10)
            
            # Add formatted data labels
            for bar in bars:
                width = bar.get_width()
                ax4.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                        f'${width:,.2f}', ha='left', va='center', fontsize=9)
        
        plt.suptitle('Medical Billing Rejection Analysis Dashboard', fontsize=16)
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        
        chart_path = charts_dir / f"{filename_prefix}_combined_dashboard.png"
        plt.savefig(chart_path, dpi=300)
        plt.close()
        logger.info(f"Generated combined dashboard at {chart_path}")
        
    except Exception as e:
        logger.error(f"Error generating advanced visualizations: {str(e)}")

def process_high_rejection_drs_format(file_path):
    """
    Special function to process the specific format of high_rejection_Drs.xlsx file
    where doctor names, medications, and rejection reasons are all in a single column.
    
    Parameters:
    -----------
    file_path : str
        Path to the Excel file.
        
    Returns:
    --------
    DataFrame: processed_data
        Properly structured DataFrame with separated columns for analysis.
    """
    try:
        logger.info(f"Processing specialized format from {file_path}")
        
        # Read the Excel file
        raw_data = pd.read_excel(file_path)
        
        if 'Row Labels' in raw_data.columns and 'Sum of Rejected Amount' in raw_data.columns:
            logger.info("Detected high_rejection_Drs.xlsx format with 'Row Labels' column")
            
            # Create a more structured dataset
            structured_data = []
            
            # Variables to track the current context
            current_doctor = None
            current_medication = None
            current_reason = None
            
            # Process each row
            for i, row in raw_data.iterrows():
                label = row['Row Labels']
                amount = row['Sum of Rejected Amount']
                
                # Skip empty rows
                if pd.isna(label) or str(label).strip() == '':
                    continue
                
                # Try to identify what type of information this row contains
                label_str = str(label).strip()
                
                # Check if it's a doctor (often has numeric identifier)
                if label_str.isdigit() or (len(label_str) >= 8 and label_str[:8].isdigit()):
                    current_doctor = label_str
                    current_medication = None
                    current_reason = None
                
                # Check if it's a medication (usually contains words like mg, ml, tablet, capsule)
                elif any(med_term in label_str.lower() for med_term in ['mg', 'ml', 'tablet', 'capsule', 'vial', 'injection', 'infusion']):
                    current_medication = label_str
                    # Don't reset current_doctor
                    current_reason = None
                
                # Otherwise assume it's a rejection reason
                else:
                    current_reason = label_str
                    # Keep current_doctor and current_medication
                
                # Only add a record if we have at least some useful information and an amount
                if (current_doctor or current_medication or current_reason) and not pd.isna(amount):
                    structured_data.append({
                        'Doctor_Code': current_doctor if current_doctor else 'Unknown',
                        'Medication': current_medication if current_medication else '',
                        'Reason': current_reason if current_reason else 'Unknown',
                        'Rejected_Amount': amount
                    })
            
            processed_data = pd.DataFrame(structured_data)
            
            # Extract diagnosis codes and categorize rejections
            processed_data['diagnosis_codes'] = processed_data['Reason'].apply(extract_diagnosis_codes)
            processed_data['medication_codes'] = processed_data['Reason'].apply(extract_medication_codes)
            processed_data['rejection_category'] = processed_data['Reason'].apply(categorize_rejection)
            
            logger.info(f"Successfully processed data into {len(processed_data)} structured records")
            logger.info(f"Created columns: {processed_data.columns.tolist()}")
            
            return processed_data
        
        # If it doesn't match the expected format, return the original data
        logger.warning("File doesn't match the expected high_rejection_Drs.xlsx format")
        return raw_data
            
    except Exception as e:
        logger.error(f"Error processing high_rejection_Drs format: {str(e)}")
        return pd.DataFrame()

def main():
    """
    Main function to run the medical billing rejection analysis workflow.
    Handles command line arguments and executes the analysis pipeline.
    """
    try:
        import argparse
        
        parser = argparse.ArgumentParser(description='Medical Billing Rejection Analysis Tool')
        parser.add_argument('--input', '-i', type=str, help='Path to the MWS Excel file')
        parser.add_argument('--output', '-o', type=str, help='Directory for output files')
        parser.add_argument('--min-rejections', '-m', type=int, default=3, 
                          help='Minimum number of rejections for a category to be included in training materials')
        
        args = parser.parse_args()
        
        # Create output directory
        output_dir = Path(args.output) if args.output else create_output_directory()
        output_dir.mkdir(exist_ok=True)
        
        logger.info("Starting medical billing rejection analysis")
        
        # If no input file specified, look for Excel files in the current directory
        if not args.input:
            excel_files = list(Path('.').glob('*.xlsx'))
            if not excel_files:
                logger.error("No Excel files found in current directory and no input file specified")
                print("Error: No Excel files found. Please specify an input file with --input")
                return
            
            # Use the first Excel file found
            input_file = str(excel_files[0])
            logger.info(f"No input file specified. Using: {input_file}")
        else:
            input_file = args.input
          # Load data from Excel file
        logger.info(f"Loading data from: {input_file}")
        
        # Check if this is the special high_rejection_Drs.xlsx format
        if "high_rejection_drs" in input_file.lower():
            logger.info("Detected high_rejection_Drs format, using specialized processing")
            rejection_data = process_high_rejection_drs_format(input_file)
        else:
            # Use standard loader for other MWS files
            rejection_data = load_mws_excel_files(input_file)
        
        if rejection_data.empty:
            logger.error("No data loaded or empty dataset. Stopping analysis.")
            return
        
        logger.info(f"Successfully loaded data with {len(rejection_data)} records")
        
        # Analyze rejections
        logger.info("Starting rejection analysis...")
        analysis_results = analyze_rejections(rejection_data)
        
        if not analysis_results:
            logger.error("Unable to proceed: Failed to analyze rejections")
            return
        
        # Generate standard reports (Excel and TXT)
        logger.info("Generating standard reports...")
        excel_report_path, txt_report_path = generate_reports(analysis_results, output_dir)
        
        if excel_report_path:
            logger.info(f"Excel report generated successfully: {excel_report_path}")
        else:
            logger.error("Failed to generate Excel report")
            
        if txt_report_path:
            logger.info(f"TXT report generated successfully: {txt_report_path}")
        else:
            logger.error("Failed to generate TXT report")
        
        # Generate advanced visualizations
        logger.info("Generating advanced visualizations...")
        generate_advanced_visualizations(analysis_results, output_dir, "advanced")
        
        # Generate advanced insights
        logger.info("Generating advanced insights and recommendations...")
        insights_path = generate_advanced_insights(analysis_results, output_dir)
        
        if insights_path:
            logger.info(f"Advanced insights report generated successfully: {insights_path}")
        else:
            logger.error("Failed to generate advanced insights report")
        
        # Prepare training materials
        logger.info("Preparing doctor-specific training materials...")
        training_path = prepare_training_materials(rejection_data, analysis_results, output_dir, args.min_rejections)
        
        if training_path:
            logger.info(f"Training materials generated successfully: {training_path}")
        else:
            logger.error("Failed to generate training materials")
            
        logger.info("Medical billing rejection analysis completed")
        
        # Print success message and output locations
        print("\n" + "="*80)
        print("MEDICAL BILLING REJECTION ANALYSIS COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Output files have been saved to: {output_dir}")
        print(f"Excel Report: {os.path.basename(excel_report_path) if excel_report_path else 'Failed to generate'}")
        print(f"Text Report: {os.path.basename(txt_report_path) if txt_report_path else 'Failed to generate'}")
        print(f"Advanced Insights: {os.path.basename(insights_path) if insights_path else 'Failed to generate'}")
        print(f"Training Materials: {os.path.basename(training_path) if training_path else 'Failed to generate'}")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
