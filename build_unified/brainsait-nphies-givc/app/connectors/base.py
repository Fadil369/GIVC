"""
Base Connector - Foundation for all portal integrations
Provides session management, retry logic, and circuit breaker pattern
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import asyncio
from functools import wraps
from app.core import log


class SessionManager:
    """Manages active sessions across all portals"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(
        self,
        portal: str,
        branch: str,
        session_data: Dict[str, Any],
        timeout: int = 3600
    ) -> str:
        """Create a new session"""
        session_id = f"{portal}_{branch}_{datetime.utcnow().timestamp()}"
        
        self.sessions[session_id] = {
            'portal': portal,
            'branch': branch,
            'data': session_data,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=timeout),
            'last_accessed': datetime.utcnow()
        }
        
        log.info(f"Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session = self.sessions.get(session_id)
        
        if session:
            # Check if expired
            if datetime.utcnow() > session['expires_at']:
                self.delete_session(session_id)
                return None
            
            # Update last accessed
            session['last_accessed'] = datetime.utcnow()
            return session
        
        return None
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id]['data'].update(session_data)
            self.sessions[session_id]['last_accessed'] = datetime.utcnow()
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            log.info(f"Session deleted: {session_id}")
            return True
        return False
    
    def cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self.sessions.items()
            if now > session['expires_at']
        ]
        
        for sid in expired:
            self.delete_session(sid)
        
        if expired:
            log.info(f"Cleaned up {len(expired)} expired sessions")
    
    def list_sessions(self, portal: Optional[str] = None) -> list:
        """List all active sessions"""
        self.cleanup_expired()
        
        if portal:
            return [
                {
                    'session_id': sid,
                    'portal': session['portal'],
                    'branch': session['branch'],
                    'created_at': session['created_at'].isoformat(),
                    'expires_at': session['expires_at'].isoformat()
                }
                for sid, session in self.sessions.items()
                if session['portal'] == portal
            ]
        
        return [
            {
                'session_id': sid,
                'portal': session['portal'],
                'branch': session['branch'],
                'created_at': session['created_at'].isoformat(),
                'expires_at': session['expires_at'].isoformat()
            }
            for sid, session in self.sessions.items()
        ]


# Global session manager instance
session_manager = SessionManager()


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        log.warning(f"Attempt {attempt}/{max_attempts} failed: {str(e)}. Retrying in {current_delay}s...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        log.error(f"All {max_attempts} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator


def circuit_breaker(failure_threshold: int = 5, timeout: int = 60):
    """Circuit breaker pattern decorator"""
    state = {
        'failures': 0,
        'last_failure_time': None,
        'is_open': False
    }
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if circuit is open
            if state['is_open']:
                # Check if timeout has passed
                if datetime.utcnow() - state['last_failure_time'] > timedelta(seconds=timeout):
                    log.info(f"Circuit breaker for {func.__name__} attempting half-open state")
                    state['is_open'] = False
                    state['failures'] = 0
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                # Success - reset failure count
                state['failures'] = 0
                return result
            
            except Exception as e:
                state['failures'] += 1
                state['last_failure_time'] = datetime.utcnow()
                
                if state['failures'] >= failure_threshold:
                    state['is_open'] = True
                    log.error(f"Circuit breaker OPENED for {func.__name__} after {state['failures']} failures")
                
                raise e
        
        return wrapper
    return decorator


class BaseConnector:
    """Base class for all portal connectors"""
    
    def __init__(
        self,
        portal_name: str,
        branch: str,
        config: Dict[str, Any]
    ):
        self.portal_name = portal_name
        self.branch = branch
        self.config = config
        
        # HTTP client
        self._client: Optional[httpx.AsyncClient] = None
        self.timeout = config.get('timeout', 30.0)
        
        # Session manager
        self.session_manager = session_manager
        
        # Circuit breaker settings
        self.circuit_failure_threshold = config.get('circuit_failure_threshold', 5)
        self.circuit_timeout = config.get('circuit_timeout', 60)
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
        
        return self._client
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    async def make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic"""
        client = await self.get_client()
        
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        
        except httpx.HTTPStatusError as e:
            log.error(f"{method} {url} failed with status {e.response.status_code}")
            raise
        
        except httpx.RequestError as e:
            log.error(f"{method} {url} failed: {str(e)}")
            raise
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to portal - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement login()")
    
    async def logout(self, session_id: str) -> bool:
        """Logout from portal - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement logout()")
    
    async def submit_claim(
        self,
        claim_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit claim - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement submit_claim()")
    
    async def get_claim_status(
        self,
        claim_id: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get claim status - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_claim_status()")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check portal health"""
        try:
            base_url = self.config.get('base_url')
            if not base_url:
                return {
                    'status': 'unknown',
                    'message': 'No base URL configured'
                }
            
            response = await self.make_request('GET', base_url)
            
            return {
                'status': 'healthy',
                'portal': self.portal_name,
                'branch': self.branch,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'checked_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                'status': 'unhealthy',
                'portal': self.portal_name,
                'branch': self.branch,
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def __repr__(self):
        return f"<{self.__class__.__name__} portal={self.portal_name} branch={self.branch}>"
