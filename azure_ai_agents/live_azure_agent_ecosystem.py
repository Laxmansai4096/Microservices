"""
===============================================================================
AZURE AI AGENTS ECOSYSTEM - REAL-TIME LIVE WORKING DEMO
===============================================================================
Features Demonstrated:
1. Dynamic Azure Authentication via active `az login` (Azure CLI / RBAC)
2. Real-time Tool Calling against Azure OpenAI / Azure AI Foundry (`gpt-5-mini`)
3. Multi-Database Connectivity:
   - Relational Database (SQL: Orders, Customers, Inventory)
   - Document NoSQL Database (Cosmos DB style: JSON Product Catalog & Specs)
   - Enterprise Knowledge Store (Azure AI Search style: Policies & RAG)
4. Agent-to-Agent (A2A) Collaboration:
   - DataAnalystAgent (SQL + NoSQL database specialist)
   - ComplianceAgent (Policy & RAG specialist)
   - LogisticsAgent (Warehouse & dispatch specialist)
   - SupervisorOrchestratorAgent (Master Orchestrator coordinating A2A workflow)
===============================================================================
"""

import json
import sqlite3
import subprocess
import sys
import time
from typing import Any, Dict, List
from openai import AzureOpenAI

# Force UTF-8 output on Windows consoles to prevent cp1252 encoding errors
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# =============================================================================
# 1. AZURE AUTHENTICATION (DYNAMIC AZ LOGIN INTEGRATION)
# =============================================================================
AZURE_ENDPOINT = "https://openai-explore-ai-65064.openai.azure.com/"
MODEL_DEPLOYMENT = "gpt-5-mini"
RESOURCE_GROUP = "rg-explore-ai"
ACCOUNT_NAME = "openai-explore-ai"

def get_azure_openai_client() -> AzureOpenAI:
    """
    Dynamically resolves credentials from the active `az login` session.
    Zero hardcoded secrets; automatically uses Azure CLI session.
    """
    print("[AUTH] [AUTH] Resolving Azure credentials via active `az login` session...")
    try:
        cmd = f"az cognitiveservices account keys list -g {RESOURCE_GROUP} -n {ACCOUNT_NAME} --query key1 -o tsv"
        key = subprocess.check_output(cmd, shell=True).decode().strip()
        if not key:
            raise ValueError("No key returned from az CLI.")
        print(f"[SUCCESS] [AUTH] Authenticated successfully via Azure CLI! Endpoint: {AZURE_ENDPOINT}")
        return AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=key,
            api_version="2024-08-01-preview"
        )
    except Exception as e:
        print(f"[ERROR] [AUTH ERROR] Failed to authenticate via az login: {e}")
        sys.exit(1)


# =============================================================================
# 2. MULTI-DATABASE LAYER (SQL + COSMOS DB NOSQL + POLICY KNOWLEDGE BASE)
# =============================================================================

# --- Database 1: Relational SQL Database (Simulating Azure SQL DB) ---
def init_relational_sql_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    
    # Tables: customers, orders, inventory
    cur.execute("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT,
            tier TEXT,
            credit_limit REAL
        )
    """)
    cur.execute("""
        CREATE TABLE inventory (
            sku TEXT PRIMARY KEY,
            product_name TEXT,
            warehouse_location TEXT,
            stock_quantity INTEGER,
            unit_price REAL
        )
    """)
    cur.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            sku TEXT,
            quantity INTEGER,
            total_amount REAL,
            order_status TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(sku) REFERENCES inventory(sku)
        )
    """)
    
    # Seed Data
    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", [
        ("CUST-101", "Global Logistics Corp", "VIP_PLATINUM", 500000.0),
        ("CUST-202", "Apex Retailers Ltd", "STANDARD", 50000.0),
    ])
    cur.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?)", [
        ("SKU-9901", "Enterprise Edge Server Pro", "Warehouse-East-US", 42, 2800.0),
        ("SKU-4420", "Industrial IoT Sensor Hub", "Warehouse-Central-US", 115, 650.0),
        ("SKU-8810", "Fiber Optics Transceiver 100G", "Warehouse-East-US", 0, 1200.0),
    ])
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", [
        ("ORD-5512", "CUST-101", "SKU-9901", 5, 14000.0, "DELIVERED"),
        ("ORD-7788", "CUST-202", "SKU-4420", 10, 6500.0, "PENDING_DISPATCH"),
    ])
    conn.commit()
    return conn

# Global In-Memory SQL DB Instance
SQL_CONN = init_relational_sql_db()

# --- Database 2: Document / NoSQL Store (Simulating Azure Cosmos DB) ---
COSMOS_NO_SQL_DB = {
    "product_specifications": {
        "SKU-9901": {
            "sku": "SKU-9901",
            "warranty_tier": "3-Year 24/7 Enterprise Onsite",
            "return_window_days": 30,
            "weight_kg": 18.5,
            "hazmat": False,
            "compatible_upgrades": ["SKU-4420", "SKU-8810"]
        },
        "SKU-4420": {
            "sku": "SKU-4420",
            "warranty_tier": "1-Year Standard Replacement",
            "return_window_days": 14,
            "weight_kg": 2.1,
            "hazmat": False,
            "compatible_upgrades": []
        }
    },
    "customer_sla_profiles": {
        "CUST-101": {
            "customer_id": "CUST-101",
            "sla_level": "Mission Critical Tier-1",
            "free_expedited_shipping": True,
            "restocking_fee_waived": True,
            "priority_dispatch": True
        },
        "CUST-202": {
            "customer_id": "CUST-202",
            "sla_level": "Standard Tier-3",
            "free_expedited_shipping": False,
            "restocking_fee_waived": False,
            "priority_dispatch": False
        }
    }
}

# --- Database 3: Policy / RAG Vector Store (Simulating Azure AI Search) ---
POLICY_KNOWLEDGE_STORE = {
    "return_policy": "VIP_PLATINUM customers are eligible for 100% refund or upgrade exchange within 60 days with waived restocking fees. Standard customers are subject to 15% restocking fee.",
    "freight_policy": "Hazardous or heavy items (>15kg) require specialized freight carrier approval if moving across warehouses.",
    "exchange_policy": "For equipment exchanges, credit is computed by subtracting the returned unit value from the new item total; customer account is credited or invoiced for delta."
}


# =============================================================================
# 3. AGENT TOOLS (SQL, COSMOS DB, POLICY RAG, DISPATCH)
# =============================================================================

def tool_execute_sql_query(query: str) -> str:
    """Executes a SELECT query against the Azure Relational SQL Database."""
    print(f"   [SQL] [TOOL: Azure SQL Database] Executing: {query}")
    cur = SQL_CONN.cursor()
    try:
        # Security sanity check
        if not query.strip().upper().startswith("SELECT"):
            return json.dumps({"error": "Only SELECT read queries are permitted."})
        cur.execute(query)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        return json.dumps({"status": "SUCCESS", "row_count": len(result), "data": result})
    except Exception as e:
        return json.dumps({"status": "ERROR", "message": str(e)})

def tool_query_cosmos_nosql(collection_name: str, document_key: str) -> str:
    """Queries a JSON document from Azure Cosmos DB collection by document key."""
    print(f"   [COSMOS] [TOOL: Azure Cosmos DB] Querying collection '{collection_name}' for key '{document_key}'")
    collection = COSMOS_NO_SQL_DB.get(collection_name)
    if not collection:
        return json.dumps({"status": "NOT_FOUND", "message": f"Collection '{collection_name}' does not exist."})
    doc = collection.get(document_key)
    if not doc:
        return json.dumps({"status": "NOT_FOUND", "message": f"Document '{document_key}' not found."})
    return json.dumps({"status": "SUCCESS", "document": doc})

def tool_search_enterprise_policies(topic: str) -> str:
    """Searches Azure AI Search enterprise policy knowledge base for regulatory rules."""
    print(f"   [RAG] [TOOL: Azure AI Search RAG] Searching enterprise policy for '{topic}'")
    results = {}
    for key, text in POLICY_KNOWLEDGE_STORE.items():
        if topic.lower() in key.lower() or any(w in text.lower() for w in topic.lower().split()):
            results[key] = text
    if not results:
        results["general"] = "Standard company operating procedures apply."
    return json.dumps({"status": "SUCCESS", "matches": results})

def tool_create_warehouse_dispatch(sku: str, quantity: int, destination: str, shipping_mode: str) -> str:
    """Triggers an automated logistics dispatch order in the warehouse fulfillment system."""
    dispatch_id = f"DSP-{int(time.time())}"
    print(f"   [LOGISTICS] [TOOL: Logistics API] Dispatch '{dispatch_id}' created: {quantity}x {sku} -> {destination} ({shipping_mode})")
    return json.dumps({
        "status": "DISPATCH_CONFIRMED",
        "dispatch_id": dispatch_id,
        "sku": sku,
        "quantity": quantity,
        "destination": destination,
        "shipping_mode": shipping_mode,
        "estimated_arrival": "24-48 Hours"
    })


# =============================================================================
# 4. SPECIALIST AGENTS IMPLEMENTATION
# =============================================================================

class SpecialistAgent:
    """Base class for Azure AI specialist agents equipped with tools and system prompt."""
    def __init__(self, name: str, role_description: str, system_prompt: str, tools: List[Dict], client: AzureOpenAI):
        self.name = name
        self.role_description = role_description
        self.system_prompt = system_prompt
        self.tools = tools
        self.client = client

    def execute(self, prompt: str) -> str:
        print(f"\n[{self.name}] Received delegation: {prompt}")
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Tool execution loop
        while True:
            response = self.client.chat.completions.create(
                model=MODEL_DEPLOYMENT,
                messages=messages,
                tools=self.tools if self.tools else None
            )
            msg = response.choices[0].message
            messages.append(msg)
            
            # If the model requested tool calls, execute them
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    print(f"[{self.name}] [ACTION] Calling Tool -> {fn_name}({fn_args})")
                    
                    # Tool router
                    if fn_name == "tool_execute_sql_query":
                        tool_res = tool_execute_sql_query(fn_args["query"])
                    elif fn_name == "tool_query_cosmos_nosql":
                        tool_res = tool_query_cosmos_nosql(fn_args["collection_name"], fn_args["document_key"])
                    elif fn_name == "tool_search_enterprise_policies":
                        tool_res = tool_search_enterprise_policies(fn_args["topic"])
                    elif fn_name == "tool_create_warehouse_dispatch":
                        tool_res = tool_create_warehouse_dispatch(
                            fn_args["sku"], fn_args["quantity"], fn_args["destination"], fn_args["shipping_mode"]
                        )
                    else:
                        tool_res = json.dumps({"error": f"Unknown tool {fn_name}"})
                        
                    # Feed tool response back to agent
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_res
                    })
            else:
                # No more tool calls; final specialist output
                final_content = msg.content or ""
                print(f"[{self.name}] [DONE] Output:\n{final_content}\n")
                return final_content


# =============================================================================
# 5. AGENT DEFINITIONS (DATABASE ANALYST, COMPLIANCE, LOGISTICS)
# =============================================================================

def build_agents(client: AzureOpenAI):
    # Agent 1: Database & Inventory Analyst Agent
    data_analyst_tools = [
        {
            "type": "function",
            "function": {
                "name": "tool_execute_sql_query",
                "description": "Execute SQL SELECT query against relational database tables (customers, orders, inventory).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL SELECT statement to execute."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "tool_query_cosmos_nosql",
                "description": "Query Azure Cosmos DB collections (product_specifications, customer_sla_profiles) by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection_name": {"type": "string", "description": "Collection name: 'product_specifications' or 'customer_sla_profiles'"},
                        "document_key": {"type": "string", "description": "The SKU or Customer ID key"}
                    },
                    "required": ["collection_name", "document_key"]
                }
            }
        }
    ]
    data_analyst = SpecialistAgent(
        name="DataAnalystAgent",
        role_description="Specialist in relational SQL queries and Cosmos DB NoSQL document lookups.",
        system_prompt=(
            "You are an Azure Enterprise Data Analyst Agent. You have direct access to relational SQL tables "
            "(customers, orders, inventory) and Cosmos DB NoSQL documents (product_specifications, customer_sla_profiles). "
            "When queried, inspect the database records, join relational information with document specs, and provide exact "
            "financial figures, quantities, pricing, and specs in a concise structured format."
        ),
        tools=data_analyst_tools,
        client=client
    )

    # Agent 2: Policy & Compliance Agent
    compliance_tools = [
        {
            "type": "function",
            "function": {
                "name": "tool_search_enterprise_policies",
                "description": "Search Azure AI Search policy store for return policies, freight regulations, and VIP clauses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Policy topic, e.g. 'return_policy', 'freight_policy', 'exchange_policy'"}
                    },
                    "required": ["topic"]
                }
            }
        }
    ]
    compliance_agent = SpecialistAgent(
        name="ComplianceAgent",
        role_description="Specialist in enterprise policy verification, return rules, and compliance audits.",
        system_prompt=(
            "You are an Azure Compliance & Governance Agent. Your role is to evaluate customer requests against "
            "corporate policies retrieved from Azure AI Search knowledge store. Verify eligibility, fee waivers, "
            "and regulatory constraints, and give a definitive COMPLIANT or NON_COMPLIANT verdict with policy reasoning."
        ),
        tools=compliance_tools,
        client=client
    )

    # Agent 3: Logistics & Fulfillment Agent
    logistics_tools = [
        {
            "type": "function",
            "function": {
                "name": "tool_create_warehouse_dispatch",
                "description": "Issue an automated dispatch order in the warehouse system for equipment shipping.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sku": {"type": "string", "description": "Product SKU to ship"},
                        "quantity": {"type": "integer", "description": "Quantity of units to dispatch"},
                        "destination": {"type": "string", "description": "Destination address or customer name"},
                        "shipping_mode": {"type": "string", "description": "Shipping mode: 'Standard Ground' or 'Priority Overnight'"}
                    },
                    "required": ["sku", "quantity", "destination", "shipping_mode"]
                }
            }
        }
    ]
    logistics_agent = SpecialistAgent(
        name="LogisticsAgent",
        role_description="Specialist in inventory dispatch and freight coordination.",
        system_prompt=(
            "You are an Azure Logistics & Fulfillment Agent. When instructed to initiate shipping or equipment replacement, "
            "trigger warehouse dispatch using your tools and report the dispatch confirmation ID and timeline."
        ),
        tools=logistics_tools,
        client=client
    )

    return data_analyst, compliance_agent, logistics_agent


# =============================================================================
# 6. SUPERVISOR ORCHESTRATOR & AGENT-TO-AGENT (A2A) SERVICE
# =============================================================================

class SupervisorOrchestrator:
    """
    Master Azure AI Orchestrator Agent.
    Implements Hierarchical Multi-Agent (A2A) Orchestration.
    Equipped with A2A delegation tools to invoke downstream specialist agents.
    """
    def __init__(self, client: AzureOpenAI, data_analyst: SpecialistAgent, compliance_agent: SpecialistAgent, logistics_agent: SpecialistAgent):
        self.client = client
        self.data_analyst = data_analyst
        self.compliance_agent = compliance_agent
        self.logistics_agent = logistics_agent
        
        # A2A Delegation Tools for the Supervisor
        self.supervisor_tools = [
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_data_analyst",
                    "description": "Call the DataAnalystAgent to query SQL orders, customer records, inventory stock, and Cosmos DB specs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instructions": {"type": "string", "description": "Detailed instructions on what database data to fetch or analyze."}
                        },
                        "required": ["instructions"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_compliance_agent",
                    "description": "Call the ComplianceAgent to verify policy compliance, return eligibility, and fee waivers.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_tier": {"type": "string", "description": "The tier of the customer, e.g., VIP_PLATINUM"},
                            "request_details": {"type": "string", "description": "Details of the exchange/return request to validate against policy."}
                        },
                        "required": ["customer_tier", "request_details"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_logistics_agent",
                    "description": "Call the LogisticsAgent to dispatch inventory items and schedule shipments.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sku": {"type": "string", "description": "The product SKU to dispatch"},
                            "quantity": {"type": "integer", "description": "Quantity to ship"},
                            "destination": {"type": "string", "description": "Recipient or company name"},
                            "shipping_mode": {"type": "string", "description": "Priority Overnight or Standard Ground"}
                        },
                        "required": ["sku", "quantity", "destination", "shipping_mode"]
                    }
                }
            }
        ]

    def run_workflow(self, user_mission: str):
        print("\n" + "=" * 90)
        print("[ORCHESTRATOR] [AZURE A2A SUPERVISOR ORCHESTRATOR] STARTING MULTI-AGENT MISSION")
        print(f"MISSION: {user_mission}")
        print("=" * 90)

        system_prompt = (
            "You are the Master Azure Orchestrator Agent. You lead an enterprise multi-agent team comprising: "
            "1. DataAnalystAgent (SQL + Cosmos DB queries) "
            "2. ComplianceAgent (Policy & RAG compliance verification) "
            "3. LogisticsAgent (Warehouse shipping dispatch) "
            "You MUST orchestrate this mission step-by-step using Agent-to-Agent (A2A) tool delegation: "
            "Step 1: Delegate to DataAnalystAgent to retrieve order, customer tier, inventory stock, and Cosmos DB specs. "
            "Step 2: Delegate to ComplianceAgent to verify if the exchange is permissible and whether fees are waived. "
            "Step 3: If compliant, delegate to LogisticsAgent to dispatch the replacement items. "
            "Step 4: Synthesize a comprehensive executive summary for the stakeholder with full audit trail."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_mission}
        ]

        step_counter = 1
        while True:
            response = self.client.chat.completions.create(
                model=MODEL_DEPLOYMENT,
                messages=messages,
                tools=self.supervisor_tools
            )
            msg = response.choices[0].message
            messages.append(msg)

            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    print(f"\n[ORCHESTRATOR] [ORCHESTRATOR STEP {step_counter}] Delegating via A2A -> {fn_name}")
                    step_counter += 1

                    # A2A Service Invocations
                    if fn_name == "delegate_to_data_analyst":
                        agent_response = self.data_analyst.execute(fn_args["instructions"])
                    elif fn_name == "delegate_to_compliance_agent":
                        sub_prompt = f"Verify request for customer tier '{fn_args.get('customer_tier')}': {fn_args.get('request_details')}"
                        agent_response = self.compliance_agent.execute(sub_prompt)
                    elif fn_name == "delegate_to_logistics_agent":
                        sub_prompt = (
                            f"Dispatch {fn_args.get('quantity')} units of {fn_args.get('sku')} to "
                            f"{fn_args.get('destination')} using mode '{fn_args.get('shipping_mode')}'."
                        )
                        agent_response = self.logistics_agent.execute(sub_prompt)
                    else:
                        agent_response = f"Unknown A2A target: {fn_name}"

                    # Feed A2A response back into Supervisor Context
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": agent_response
                    })
            else:
                # Orchestrator Final Synthesis
                print("\n" + "=" * 90)
                print("[TARGET] [FINAL MULTI-AGENT EXECUTIVE RESOLUTION]")
                print("=" * 90)
                print(msg.content)
                print("=" * 90 + "\n")
                break


# =============================================================================
# 7. MAIN EXECUTION DEMO
# =============================================================================

if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("[START] INITIALIZING AZURE AI AGENTS & MULTI-DATABASE A2A ECOSYSTEM")
    print("#" * 80)

    # Step 1: Connect to Azure using az login session
    azure_client = get_azure_openai_client()

    # Step 2: Build Specialist Agents
    data_agent, comp_agent, log_agent = build_agents(azure_client)

    # Step 3: Build Master Orchestrator
    orchestrator = SupervisorOrchestrator(
        client=azure_client,
        data_analyst=data_agent,
        compliance_agent=comp_agent,
        logistics_agent=log_agent
    )

    # Step 4: Run Real-World End-to-End Enterprise Scenario
    mission = (
        "Customer 'CUST-101' (Global Logistics Corp) ordered 5 units of 'SKU-9901' under order 'ORD-5512'. "
        "They are requesting an equipment exchange: return 2 units of 'SKU-9901' and upgrade to 4 units of 'SKU-4420'. "
        "Investigate the SQL order history, check Cosmos DB product specifications and SLA profiles, verify compliance "
        "and fee waiver policies, and if approved, dispatch the replacement units from the warehouse with priority shipping."
    )

    orchestrator.run_workflow(mission)
