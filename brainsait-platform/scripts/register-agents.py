#!/usr/bin/env python3
"""
Register initial LINC agents in the OID Registry
"""

import requests
import json
import time

REGISTRY_URL = "http://localhost:8010"

# Define all 7 LINC agents
agents = [
    {
        "oid": "1.3.6.1.4.1.61026.2.1",
        "name": "systemlinc",
        "domain": "system",
        "version": "1.0.0",
        "endpoints": {"rest": "http://localhost:8010"},
        "capabilities": ["health", "config", "registry"],
        "dependencies": [],
        "status": "active"
    },
    {
        "oid": "1.3.6.1.4.1.61026.3.5",
        "name": "nphieslinc",
        "domain": "data",
        "version": "2.1.0",
        "endpoints": {"rest": "http://localhost:8020"},
        "capabilities": ["validate", "submit", "track"],
        "dependencies": [],
        "status": "active"
    },
    {
        "oid": "1.3.6.1.4.1.61026.4.2",
        "name": "claimlinc",
        "domain": "healthcare",
        "version": "1.0.0",
        "endpoints": {"rest": "http://localhost:3000/api/claims"},
        "capabilities": ["submit", "track", "appeal"],
        "dependencies": ["1.3.6.1.4.1.61026.3.5"],
        "status": "active"
    },
    {
        "oid": "1.3.6.1.4.1.61026.5.1",
        "name": "paymentlinc",
        "domain": "business",
        "version": "1.5.0",
        "endpoints": {"rest": "http://localhost:8050"},
        "capabilities": ["charge", "refund", "validate"],
        "dependencies": [],
        "status": "active"
    },
    {
        "oid": "1.3.6.1.4.1.61026.6.1",
        "name": "templatelinc",
        "domain": "creative",
        "version": "1.0.0",
        "endpoints": {"rest": "http://localhost:8030"},
        "capabilities": ["sync", "search", "analyze"],
        "dependencies": [],
        "status": "active"
    },
    {
        "oid": "1.3.6.1.4.1.61026.7.1",
        "name": "chatlinc",
        "domain": "user",
        "version": "1.0.0",
        "endpoints": {"websocket": "ws://localhost:8040/chat"},
        "capabilities": ["chat", "regenerate", "recommend"],
        "dependencies": ["1.3.6.1.4.1.61026.6.1", "1.3.6.1.4.1.61026.3.5"],
        "status": "active"
    },
    {
        "oid": "1.3.6.1.4.1.61026.8.1",
        "name": "comasterlinc",
        "domain": "master",
        "version": "1.0.0",
        "endpoints": {"rest": "http://localhost:8000"},
        "capabilities": ["orchestrate", "monitor", "alert"],
        "dependencies": [],
        "status": "active"
    }
]

def register_agents():
    print("🔐 Registering LINC Agents in OID Registry...")
    print("=" * 60)
    
    # Wait for registry to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{REGISTRY_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ OID Registry is ready")
                break
        except:
            print(f"⏳ Waiting for OID Registry... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("❌ OID Registry not available. Exiting.")
        return
    
    print()
    
    # Register each agent
    for agent in agents:
        try:
            response = requests.post(
                f"{REGISTRY_URL}/api/v1/registry/agents",
                json=agent,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Registered: {agent['name']} ({agent['oid']})")
            elif response.status_code == 409:
                print(f"⚠️  Already exists: {agent['name']} ({agent['oid']})")
            else:
                print(f"❌ Failed to register {agent['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
        
        except Exception as e:
            print(f"❌ Error registering {agent['name']}: {str(e)}")
    
    print()
    print("=" * 60)
    print("✨ Agent registration complete!")
    print()
    
    # Verify by listing all agents
    try:
        response = requests.get(f"{REGISTRY_URL}/api/v1/registry/agents")
        if response.status_code == 200:
            registered = response.json()
            print(f"📊 Total agents registered: {len(registered)}")
            print()
            print("Agents by domain:")
            domains = {}
            for agent in registered:
                domain = agent.get('domain', 'unknown')
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(agent['name'])
            
            for domain, agents in sorted(domains.items()):
                print(f"  {domain}: {', '.join(agents)}")
    except Exception as e:
        print(f"⚠️  Could not verify registration: {str(e)}")

if __name__ == "__main__":
    register_agents()
