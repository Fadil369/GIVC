#!/usr/bin/env python3
"""
🔗 BrainSAIT Platform - Integration Enhancement Script
Adds cross-service integration capabilities
"""

import httpx
import asyncio
import json
from typing import Dict, Any

# Service URLs
REGISTRY_URL = "http://localhost:8010"
MCP_URL = "http://localhost:8020"
TEMPLATE_URL = "http://localhost:8030"
CHAT_URL = "http://localhost:8040"
PAYMENT_URL = "http://localhost:8050"


class IntegrationEnhancer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_chat_template_integration(self):
        """Test chat engine calling template engine"""
        print("🔗 Testing Chat ←→ Template Integration...")
        
        # Simulate chat requesting a template
        workflow = [
            {
                "agent": "1.3.6.1.4.1.61026.6.1",  # Template Engine
                "action": "search",
                "params": {
                    "query": "healthcare claim",
                    "category": "healthcare",
                    "limit": 5
                }
            }
        ]
        
        try:
            response = await self.client.post(
                f"{MCP_URL}/orchestrate",
                json=workflow
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Chat can access templates via MCP")
                print(f"     Status: {result.get('status')}")
                return True
            else:
                print(f"  ❌ Integration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    async def test_chat_payment_integration(self):
        """Test chat engine triggering payment"""
        print("🔗 Testing Chat ←→ Payment Integration...")
        
        workflow = [
            {
                "agent": "1.3.6.1.4.1.61026.5.1",  # Payment Engine
                "action": "validate",
                "params": {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 25,
                    "cvv": "123"
                }
            }
        ]
        
        try:
            response = await self.client.post(
                f"{MCP_URL}/orchestrate",
                json=workflow
            )
            
            if response.status_code == 200:
                print(f"  ✅ Chat can validate payments via MCP")
                return True
            else:
                print(f"  ❌ Integration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    async def test_multi_agent_workflow(self):
        """Test complex multi-agent workflow"""
        print("🔗 Testing Multi-Agent Workflow...")
        print("   Scenario: User wants to submit claim → find template → process payment")
        
        workflow = [
            {
                "agent": "1.3.6.1.4.1.61026.6.1",  # Template Engine
                "action": "search",
                "params": {
                    "query": "medical claim",
                    "category": "healthcare",
                    "limit": 1
                }
            },
            {
                "agent": "1.3.6.1.4.1.61026.5.1",  # Payment Engine
                "action": "validate",
                "params": {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 26,
                    "cvv": "123"
                }
            }
        ]
        
        try:
            response = await self.client.post(
                f"{MCP_URL}/orchestrate",
                json=workflow
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Multi-agent workflow executed")
                print(f"     Status: {result.get('status')}")
                print(f"     Steps completed: {len(result.get('results', []))}")
                return True
            else:
                print(f"  ❌ Workflow failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    async def verify_all_agents_registered(self):
        """Verify all agents are properly registered"""
        print("📋 Verifying Agent Registration...")
        
        try:
            response = await self.client.get(f"{REGISTRY_URL}/api/v1/registry/agents")
            
            if response.status_code == 200:
                agents = response.json()
                print(f"  ✅ {len(agents)} agents registered")
                
                expected_oids = [
                    "1.3.6.1.4.1.61026.2.1",  # SystemLINC
                    "1.3.6.1.4.1.61026.5.1",  # PaymentLINC
                    "1.3.6.1.4.1.61026.6.1",  # TemplateLINC
                    "1.3.6.1.4.1.61026.7.1",  # ChatLINC
                    "1.3.6.1.4.1.61026.8.1",  # CoMasterLINC (MCP)
                ]
                
                registered_oids = [agent['oid'] for agent in agents]
                
                for oid in expected_oids:
                    if oid in registered_oids:
                        agent = next(a for a in agents if a['oid'] == oid)
                        print(f"     ✅ {agent['name']} ({oid})")
                    else:
                        print(f"     ⚠️  Missing: {oid}")
                
                return True
            else:
                print(f"  ❌ Failed to fetch agents: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    async def test_service_dependencies(self):
        """Test that services can find their dependencies"""
        print("🔍 Testing Service Dependencies...")
        
        # Test ChatLINC dependencies (should depend on TemplateLINC)
        try:
            chat_oid = "1.3.6.1.4.1.61026.7.1"
            response = await self.client.get(
                f"{REGISTRY_URL}/api/v1/registry/depends/{chat_oid}"
            )
            
            if response.status_code == 200:
                result = response.json()
                deps = result.get('dependencies', [])
                print(f"  ✅ ChatLINC dependencies: {len(deps)} found")
                for dep in deps:
                    print(f"     → {dep['name']} ({dep['oid']})")
                return True
            else:
                print(f"  ❌ Failed to get dependencies: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    async def check_all_services_healthy(self):
        """Check health status of all services"""
        print("🏥 Checking Service Health...")
        
        services = {
            "OID Registry": f"{REGISTRY_URL}/health",
            "MCP Gateway": f"{MCP_URL}/health",
            "Template Engine": f"{TEMPLATE_URL}/health",
            "Chat Engine": f"{CHAT_URL}/health",
            "Payment Engine": f"{PAYMENT_URL}/health",
        }
        
        all_healthy = True
        
        for name, url in services.items():
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    if status == 'healthy':
                        print(f"  ✅ {name}: {status}")
                    else:
                        print(f"  ⚠️  {name}: {status}")
                        all_healthy = False
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
                    all_healthy = False
            except Exception as e:
                print(f"  ❌ {name}: {str(e)}")
                all_healthy = False
        
        return all_healthy
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("🧠 BrainSAIT Platform - Integration Enhancement Tests")
        print("=" * 60)
        print()
        
        results = {}
        
        # 1. Check health
        results['health'] = await self.check_all_services_healthy()
        print()
        
        # 2. Verify agents
        results['agents'] = await self.verify_all_agents_registered()
        print()
        
        # 3. Test dependencies
        results['dependencies'] = await self.test_service_dependencies()
        print()
        
        # 4. Test chat-template integration
        results['chat_template'] = await self.test_chat_template_integration()
        print()
        
        # 5. Test chat-payment integration
        results['chat_payment'] = await self.test_chat_payment_integration()
        print()
        
        # 6. Test multi-agent workflow
        results['multi_agent'] = await self.test_multi_agent_workflow()
        print()
        
        # Summary
        print("=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test:20s}: {status}")
        
        print()
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("✨ All integration tests passed! Platform is ready.")
        else:
            print("⚠️  Some tests failed. Please review the errors above.")
        
        await self.client.aclose()
        
        return passed == total


async def main():
    enhancer = IntegrationEnhancer()
    success = await enhancer.run_all_tests()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
