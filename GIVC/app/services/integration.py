"""
Enhanced Integration Service
Orchestrates NPHIES, GIVC AI, and legacy portal connectors
"""
from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from datetime import datetime
from app.core import log
from app.services.givc import GIVCService


class SubmissionStrategy(str, Enum):
    """Claim submission strategies"""
    NPHIES_ONLY = "nphies_only"
    LEGACY_ONLY = "legacy_only"
    NPHIES_FIRST = "nphies_first"  # Try NPHIES, fallback to legacy
    ALL_PORTALS = "all_portals"  # Submit to all configured portals
    SMART_ROUTE = "smart_route"  # AI-based routing


class ConnectorFactory:
    """Factory for creating portal connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._connectors: Dict[str, Any] = {}
    
    def get_connector(self, portal: str, branch: Optional[str] = None):
        """Get or create connector instance"""
        key = f"{portal}_{branch}" if branch else portal
        
        if key not in self._connectors:
            self._connectors[key] = self._create_connector(portal, branch)
        
        return self._connectors[key]
    
    def _create_connector(self, portal: str, branch: Optional[str] = None):
        """Create new connector instance"""
        from app.connectors.nphies import NPHIESConnector
        
        if portal == "nphies":
            nphies_config = self.config.get('nphies', {})
            return NPHIESConnector(
                environment=branch or "production",
                config=nphies_config
            )
        
        elif portal == "oases":
            from app.connectors.oases import OASESConnector
            branch_config = self.config.get('oases', {}).get('branches', {}).get(branch, {})
            return OASESConnector(branch=branch, config=branch_config)
        
        elif portal == "moh":
            from app.connectors.moh import MOHConnector
            moh_config = self.config.get('moh', {})
            return MOHConnector(portal_type=branch or "approval", config=moh_config)
        
        elif portal == "jisr":
            from app.connectors.jisr import JisrConnector
            jisr_config = self.config.get('jisr', {})
            return JisrConnector(config=jisr_config)
        
        elif portal == "bupa":
            from app.connectors.bupa import BupaConnector
            bupa_config = self.config.get('bupa', {})
            return BupaConnector(config=bupa_config)
        
        else:
            raise ValueError(f"Unknown portal: {portal}")
    
    async def close_all(self):
        """Close all connectors"""
        for connector in self._connectors.values():
            await connector.close()


class IntegrationService:
    """
    Enhanced Integration Service
    Orchestrates NPHIES, GIVC AI, and legacy portals
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connector_factory = ConnectorFactory(config)
        
        # Initialize GIVC service
        givc_config = config.get('givc', {})
        self.givc_service = GIVCService(givc_config)
        
        # Default strategy
        self.default_strategy = SubmissionStrategy(
            config.get('default_strategy', 'nphies_first')
        )
    
    async def submit_claim(
        self,
        claim_data: Dict[str, Any],
        strategy: Optional[SubmissionStrategy] = None,
        portals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Submit claim with AI validation and smart routing
        
        Args:
            claim_data: Claim information
            strategy: Submission strategy (default: nphies_first)
            portals: List of specific portals to submit to
        
        Returns:
            Dict with submission results
        """
        log.info(f"Submitting claim with strategy: {strategy or self.default_strategy}")
        
        # Step 1: AI Validation with GIVC
        validation_result = await self.givc_service.validate_claim_with_ai(claim_data)
        
        if not validation_result['is_valid']:
            log.warning(f"Claim validation failed: {validation_result['errors']}")
            return {
                'success': False,
                'stage': 'validation',
                'validation': validation_result,
                'message': 'Claim failed AI validation'
            }
        
        if validation_result['confidence'] < 0.7:
            log.warning(f"Low validation confidence: {validation_result['confidence']}")
        
        # Step 2: AI Optimization
        optimization_result = await self.givc_service.optimize_claim(claim_data)
        if optimization_result['success'] and optimization_result['optimizations']:
            log.info(f"AI suggested {len(optimization_result['optimizations'])} optimizations")
            # Use optimized data if available
            claim_data = optimization_result.get('optimized_data', claim_data)
        
        # Step 3: Determine submission strategy
        strategy = strategy or self.default_strategy
        
        if strategy == SubmissionStrategy.SMART_ROUTE:
            strategy = self._determine_smart_route(claim_data)
            log.info(f"Smart routing selected strategy: {strategy}")
        
        # Step 4: Execute submission based on strategy
        if strategy == SubmissionStrategy.NPHIES_ONLY:
            result = await self._submit_to_nphies(claim_data)
        
        elif strategy == SubmissionStrategy.LEGACY_ONLY:
            result = await self._submit_to_legacy(claim_data, portals)
        
        elif strategy == SubmissionStrategy.NPHIES_FIRST:
            result = await self._submit_nphies_first(claim_data, portals)
        
        elif strategy == SubmissionStrategy.ALL_PORTALS:
            result = await self._submit_to_all(claim_data, portals)
        
        else:
            result = {
                'success': False,
                'error': f'Unknown strategy: {strategy}'
            }
        
        # Add validation and optimization info
        result['validation'] = validation_result
        result['optimization'] = optimization_result
        
        return result
    
    def _determine_smart_route(self, claim_data: Dict[str, Any]) -> SubmissionStrategy:
        """AI-based routing decision"""
        # Check insurance type
        insurance_id = claim_data.get('insurance_id', '')
        
        # TAWUNIYA policies (from config) -> NPHIES
        if any(policy in insurance_id for policy in ['BALSAM_GOLD']):
            return SubmissionStrategy.NPHIES_ONLY
        
        # Bupa policies -> Bupa portal + NPHIES
        if 'BUPA' in insurance_id.upper():
            return SubmissionStrategy.ALL_PORTALS
        
        # Default: NPHIES first with fallback
        return SubmissionStrategy.NPHIES_FIRST
    
    async def _submit_to_nphies(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit to NPHIES only"""
        try:
            connector = self.connector_factory.get_connector('nphies')
            
            # Ensure authenticated
            login_result = await connector.login()
            if not login_result['success']:
                return {
                    'success': False,
                    'stage': 'authentication',
                    'error': 'NPHIES authentication failed'
                }
            
            # Submit claim
            result = await connector.submit_claim(claim_data, login_result['session_id'])
            
            return {
                'success': result['success'],
                'stage': 'submission',
                'portals': ['nphies'],
                'results': {
                    'nphies': result
                }
            }
        
        except Exception as e:
            log.error(f"NPHIES submission failed: {str(e)}")
            return {
                'success': False,
                'stage': 'submission',
                'error': str(e)
            }
    
    async def _submit_to_legacy(
        self,
        claim_data: Dict[str, Any],
        portals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Submit to legacy portals only"""
        # Default legacy portals
        if not portals:
            portals = ['oases', 'moh']
        
        results = {}
        tasks = []
        
        for portal in portals:
            if portal == 'oases':
                # Submit to all OASES branches
                for branch in ['riyadh', 'madinah', 'unaizah', 'khamis', 'jizan', 'abha']:
                    task = self._submit_to_portal(portal, claim_data, branch)
                    tasks.append((f'oases_{branch}', task))
            else:
                task = self._submit_to_portal(portal, claim_data)
                tasks.append((portal, task))
        
        # Execute in parallel
        portal_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (portal_key, _), result in zip(tasks, portal_results):
            if isinstance(result, Exception):
                results[portal_key] = {
                    'success': False,
                    'error': str(result)
                }
            else:
                results[portal_key] = result
        
        # Check if any succeeded
        success = any(r.get('success') for r in results.values())
        
        return {
            'success': success,
            'stage': 'submission',
            'portals': portals,
            'results': results
        }
    
    async def _submit_nphies_first(
        self,
        claim_data: Dict[str, Any],
        fallback_portals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Submit to NPHIES first, fallback to legacy if fails"""
        # Try NPHIES
        nphies_result = await self._submit_to_nphies(claim_data)
        
        if nphies_result['success']:
            return nphies_result
        
        # NPHIES failed, try legacy
        log.warning("NPHIES submission failed, falling back to legacy portals")
        
        legacy_result = await self._submit_to_legacy(claim_data, fallback_portals)
        
        return {
            'success': legacy_result['success'],
            'stage': 'submission',
            'strategy': 'nphies_first_fallback',
            'nphies_result': nphies_result,
            'legacy_result': legacy_result
        }
    
    async def _submit_to_all(
        self,
        claim_data: Dict[str, Any],
        portals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Submit to all portals in parallel"""
        all_portals = portals or ['nphies', 'oases', 'moh', 'jisr', 'bupa']
        
        # Submit to NPHIES and legacy in parallel
        nphies_task = self._submit_to_nphies(claim_data) if 'nphies' in all_portals else None
        legacy_portals = [p for p in all_portals if p != 'nphies']
        legacy_task = self._submit_to_legacy(claim_data, legacy_portals) if legacy_portals else None
        
        results = {}
        
        if nphies_task and legacy_task:
            nphies_result, legacy_result = await asyncio.gather(nphies_task, legacy_task)
            results.update(nphies_result.get('results', {}))
            results.update(legacy_result.get('results', {}))
        elif nphies_task:
            nphies_result = await nphies_task
            results.update(nphies_result.get('results', {}))
        elif legacy_task:
            legacy_result = await legacy_task
            results.update(legacy_result.get('results', {}))
        
        success = any(r.get('success') for r in results.values())
        
        return {
            'success': success,
            'stage': 'submission',
            'portals': all_portals,
            'results': results
        }
    
    async def _submit_to_portal(
        self,
        portal: str,
        claim_data: Dict[str, Any],
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit to specific portal"""
        try:
            connector = self.connector_factory.get_connector(portal, branch)
            
            # Login
            username = self.config.get(portal, {}).get('username')
            password = self.config.get(portal, {}).get('password')
            
            if branch:
                branch_config = self.config.get(portal, {}).get('branches', {}).get(branch, {})
                username = branch_config.get('username', username)
                password = branch_config.get('password', password)
            
            login_result = await connector.login(username, password)
            
            if not login_result.get('success'):
                return {
                    'success': False,
                    'error': 'Login failed'
                }
            
            # Submit claim
            result = await connector.submit_claim(claim_data, login_result.get('session_id'))
            
            return result
        
        except Exception as e:
            log.error(f"Portal {portal} submission failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_eligibility(
        self,
        patient_id: str,
        insurance_id: str,
        service_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check patient eligibility via NPHIES"""
        try:
            connector = self.connector_factory.get_connector('nphies')
            result = await connector.check_eligibility(patient_id, insurance_id, service_date)
            return result
        
        except Exception as e:
            log.error(f"Eligibility check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_prior_authorization(
        self,
        patient_id: str,
        insurance_id: str,
        services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create prior authorization via NPHIES"""
        try:
            # Validate with GIVC first
            claim_data = {
                'patient_id': patient_id,
                'insurance_id': insurance_id,
                'items': services
            }
            
            validation = await self.givc_service.validate_claim_with_ai(claim_data)
            
            if not validation['is_valid']:
                return {
                    'success': False,
                    'stage': 'validation',
                    'validation': validation
                }
            
            connector = self.connector_factory.get_connector('nphies')
            result = await connector.create_prior_authorization(patient_id, insurance_id, services)
            
            result['validation'] = validation
            return result
        
        except Exception as e:
            log.error(f"Prior authorization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_claim_status(
        self,
        claim_id: str,
        portal: str = 'nphies',
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get claim status from specified portal"""
        try:
            connector = self.connector_factory.get_connector(portal, branch)
            result = await connector.get_claim_status(claim_id)
            return result
        
        except Exception as e:
            log.error(f"Get claim status failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def batch_submit(
        self,
        claims: List[Dict[str, Any]],
        strategy: Optional[SubmissionStrategy] = None
    ) -> Dict[str, Any]:
        """Submit multiple claims in batch"""
        log.info(f"Batch submitting {len(claims)} claims...")
        
        # Submit all claims in parallel
        tasks = [
            self.submit_claim(claim, strategy)
            for claim in claims
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('success'))
        failed = len(claims) - successful
        
        return {
            'success': True,
            'total_claims': len(claims),
            'successful': successful,
            'failed': failed,
            'results': [
                r if not isinstance(r, Exception) else {'success': False, 'error': str(r)}
                for r in results
            ]
        }
    
    async def health_check(self, portal: Optional[str] = None) -> Dict[str, Any]:
        """Check health of all or specific portal"""
        if portal:
            connector = self.connector_factory.get_connector(portal)
            return await connector.health_check()
        
        # Check all portals
        portals = ['nphies', 'oases', 'moh', 'jisr', 'bupa']
        health_results = {}
        
        for p in portals:
            try:
                connector = self.connector_factory.get_connector(p)
                health_results[p] = await connector.health_check()
            except Exception as e:
                health_results[p] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'overall_status': 'healthy' if all(
                h.get('status') == 'healthy' for h in health_results.values()
            ) else 'degraded',
            'portals': health_results,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close all connections"""
        await self.connector_factory.close_all()
        await self.givc_service.close()
