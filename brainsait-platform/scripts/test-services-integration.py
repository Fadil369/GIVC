#!/usr/bin/env python3
"""
Test integration between all BrainSAIT services
"""

import requests
import json
import time
from typing import Dict, Any

# Service endpoints
SERVICES = {
    "oid-registry": "http://localhost:8010",
    "mcp-gateway": "http://localhost:8020",
    "template-engine": "http://localhost:8030",
    "chat-engine": "http://localhost:8040",
    "payment-engine": "http://localhost:8050",
}

def test_service_health(name: str, url: str) -> bool:
    """Test if service is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: {data.get('status', 'healthy')}")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def test_template_workflow():
    """Test template creation and retrieval"""
    print("\n🧪 Testing Template Workflow...")
    
    # Create a template
    template = {
        "title": "Healthcare Claim Template",
        "content": "This is a test healthcare claim template",
        "category": "healthcare",
        "tags": ["claim", "nphies", "medical"]
    }
    
    try:
        response = requests.post(
            f"{SERVICES['template-engine']}/api/v1/templates",
            json=template,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            template_id = data["template"]["id"]
            print(f"  ✅ Template created: {template_id}")
            
            # Retrieve template
            response = requests.get(
                f"{SERVICES['template-engine']}/api/v1/templates/{template_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"  ✅ Template retrieved successfully")
                return True
            else:
                print(f"  ❌ Failed to retrieve template")
                return False
        else:
            print(f"  ❌ Failed to create template: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Template workflow failed: {str(e)}")
        return False

def test_payment_workflow():
    """Test payment processing"""
    print("\n🧪 Testing Payment Workflow...")
    
    # Validate a card
    card_validation = {
        "card_number": "4111111111111111",
        "exp_month": 12,
        "exp_year": 25,
        "cvv": "123"
    }
    
    try:
        response = requests.post(
            f"{SERVICES['payment-engine']}/api/v1/payments/validate",
            json=card_validation,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                print(f"  ✅ Card validated: {data.get('card_type')}")
            else:
                print(f"  ❌ Card validation failed")
                return False
        else:
            print(f"  ❌ Card validation error: {response.status_code}")
            return False
        
        # Create a payment
        payment_intent = {
            "amount": 250.00,
            "currency": "SAR",
            "gateway": "stripe",
            "description": "Integration test payment"
        }
        
        response = requests.post(
            f"{SERVICES['payment-engine']}/api/v1/payments/charge",
            json=payment_intent,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            payment_id = data["payment"]["id"]
            print(f"  ✅ Payment processed: {payment_id}")
            return True
        else:
            print(f"  ❌ Payment failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Payment workflow failed: {str(e)}")
        return False

def test_agent_registration():
    """Test agent registration in OID Registry"""
    print("\n🧪 Testing Agent Registration...")
    
    try:
        response = requests.get(
            f"{SERVICES['oid-registry']}/api/v1/registry/agents",
            timeout=5
        )
        
        if response.status_code == 200:
            agents = response.json()
            print(f"  ✅ Found {len(agents)} registered agents")
            
            # Check for specific agents
            agent_names = [a.get("name") for a in agents]
            required_agents = ["templatelinc", "paymentlinc", "chatlinc"]
            
            for agent in required_agents:
                if agent in agent_names:
                    print(f"  ✅ {agent} registered")
                else:
                    print(f"  ⚠️  {agent} not registered")
            
            return True
        else:
            print(f"  ❌ Failed to fetch agents: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Agent registration check failed: {str(e)}")
        return False

def test_mcp_gateway_routing():
    """Test MCP Gateway message routing"""
    print("\n🧪 Testing MCP Gateway Routing...")
    
    try:
        response = requests.get(
            f"{SERVICES['mcp-gateway']}/agents",
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"  ✅ MCP Gateway can list agents")
            return True
        else:
            print(f"  ❌ MCP Gateway routing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ MCP Gateway test failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🧠 BrainSAIT Platform Integration Tests")
    print("=" * 60)
    
    # Test service health
    print("\n1️⃣  Testing Service Health...")
    print("-" * 60)
    health_results = {}
    for name, url in SERVICES.items():
        health_results[name] = test_service_health(name, url)
    
    # Only continue if all services are healthy
    if not all(health_results.values()):
        print("\n❌ Some services are not healthy. Fix issues before continuing.")
        return False
    
    # Run integration tests
    print("\n2️⃣  Running Integration Tests...")
    print("-" * 60)
    
    test_results = {
        "Agent Registration": test_agent_registration(),
        "MCP Gateway Routing": test_mcp_gateway_routing(),
        "Template Workflow": test_template_workflow(),
        "Payment Workflow": test_payment_workflow()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print("-" * 60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
