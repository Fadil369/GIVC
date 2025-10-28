"""
Unit tests for authentication manager
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from auth.auth_manager import AuthenticationManager


class TestAuthenticationManager:
    """Test suite for AuthenticationManager"""
    
    def test_initialization(self):
        """Test AuthenticationManager initialization"""
        auth_manager = AuthenticationManager()
        assert auth_manager is not None
        assert auth_manager.session is not None
    
    def test_session_headers(self):
        """Test that session has correct headers"""
        auth_manager = AuthenticationManager()
        headers = auth_manager.session.headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/fhir+json"
    
    @patch('requests.Session.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        auth_manager = AuthenticationManager()
        result = auth_manager.test_connection()
        assert result is True
    
    @patch('requests.Session.get')
    def test_test_connection_failure(self, mock_get):
        """Test failed connection test"""
        mock_get.side_effect = Exception("Connection failed")
        
        auth_manager = AuthenticationManager()
        result = auth_manager.test_connection()
        assert result is False
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response
        
        auth_manager = AuthenticationManager()
        response = auth_manager.make_request("GET", "http://test.com")
        assert response is not None
        assert response.status_code == 200
    
    @patch('requests.Session.request')
    def test_make_request_with_retry(self, mock_request):
        """Test request with retry on failure"""
        # First call fails, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_request.side_effect = [mock_response_fail, mock_response_success]
        
        auth_manager = AuthenticationManager()
        response = auth_manager.make_request("GET", "http://test.com")
        assert response.status_code == 200
