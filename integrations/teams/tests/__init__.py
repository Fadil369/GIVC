"""
Unit tests for Microsoft Teams integration
Run with: pytest integrations/teams/tests/ -v --cov=integrations.teams
"""

# Test configuration
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
