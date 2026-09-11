import json
import time

# ==============================================================================
# 🛠️ TIER 1: SECURE ENTERPRISE TOOLS
# ==============================================================================

def tool_database_lookup(user_id: str) -> str:
    """Simulates querying an enterprise SQL database via Azure Function tool."""
    print(f"   [TOOL: SQL Database] Looking up financial profile for user '{user_id}'...")
    db_records = {
        "USR-8921": {"name": "Acme Corp", "annual_revenue": 1250000, "debt": 350000, "credit_score": 780},
        "USR-4011": {"name": "Beta Startups", "annual_revenue": 150000, "debt": 220000, "credit_score": 590}
    }
    record = db_records.get(user_id, {"error": "User not found"})
    return json.dumps(record)

def tool_dynamic_code_interpreter(python_code: str) -> str:
    """Simulates executing code inside an Azure Container Apps Dynamic Session Sandbox."""
    print(f"   [TOOL: Dynamic Code Sandbox] Executing math computation safely...")
    # Safe computation simulation
    scope = {}
    exec(python_code, scope)
    result = scope.get("result", "Computed successfully")
    return json.dumps({"status": "SUCCESS", "calculated_output": result})

def tool_regulatory_rag_search(query: str) -> str:
    """Simulates an Azure AI Search Vector Hybrid query over banking regulations."""
    print(f"   [TOOL: Azure AI Search RAG] Searching regulatory guidelines for '{query}'...")
    return json.dumps({
        "policy": "Federal Lending Regulation B-102",
        "max_debt_to_income_ratio": 0.43,
        "min_credit_score_for_unsecured_loan": 670,
        "mandatory_human_approval_threshold_usd": 100000
    })

# ==============================================================================
# 🤖 TIER 2: SPECIALIST AGENTS
# ==============================================================================

class FinancialAnalysisAgent:
    def analyze(self, user_id: str):
        print(f"\n[AGENT: Financial Analysis Agent] Assessing balance sheet for {user_id}...")
        # Step 1: Query database
        user_data = json.loads(tool_database_lookup(user_id))
        rev = user_data["annual_revenue"]
        debt = user_data["debt"]
        
        # Step 2: Use Python code interpreter tool to calculate exact ratio
        calc_code = f"result = round({debt} / {rev}, 4)"
        calc_res = json.loads(tool_dynamic_code_interpreter(calc_code))
        dti_ratio = calc_res["calculated_output"]
        
        print(f"   [AGENT OUTPUT] Verified Revenue: ${rev:,} | Debt: ${debt:,} | DTI Ratio: {dti_ratio * 100:.2f}%")
        return {
            "name": user_data["name"],
            "dti_ratio": dti_ratio,
            "credit_score": user_data["credit_score"]
        }

class ComplianceAgent:
    def check_compliance(self, financial_profile: dict, requested_amount: float):
        print(f"\n[AGENT: Compliance & Policy Agent] Checking Federal Lending Rules...")
        policy_data = json.loads(tool_regulatory_rag_search("loan debt to income policy"))
        
        max_dti = policy_data["max_debt_to_income_ratio"]
        min_credit = policy_data["min_credit_score_for_unsecured_loan"]
        approval_threshold = policy_data["mandatory_human_approval_threshold_usd"]
        
        passed_dti = financial_profile["dti_ratio"] <= max_dti
        passed_credit = financial_profile["credit_score"] >= min_credit
        requires_human_approval = requested_amount >= approval_threshold
        
        status = "COMPLIANT" if (passed_dti and passed_credit) else "NON_COMPLIANT"
        print(f"   [AGENT OUTPUT] Policy Status: {status} | Requires Executive Signoff: {requires_human_approval}")
        
        return {
            "compliance_status": status,
            "requires_human_approval": requires_human_approval,
            "reason": f"DTI is {financial_profile['dti_ratio']*100:.1f}% (limit {max_dti*100}%), Credit Score is {financial_profile['credit_score']} (min {min_credit})"
        }

# ==============================================================================
# 👑 TIER 3: SUPERVISOR & HUMAN-IN-THE-LOOP ORCHESTRATOR
# ==============================================================================

class SupervisorOrchestrator:
    def __init__(self):
        self.financial_agent = FinancialAnalysisAgent()
        self.compliance_agent = ComplianceAgent()

    def run_loan_approval_pipeline(self, user_id: str, loan_amount: float):
        print("=" * 80)
        print("[ORCHESTRATOR] STARTING MULTI-AGENT PIPELINE FOR LOAN AUDIT")
        print(f"Applicant ID : {user_id}")
        print(f"Loan Amount  : ${loan_amount:,.2f}")
        print("=" * 80)

        # 1. Delegate to Financial Agent
        fin_results = self.financial_agent.analyze(user_id)

        # 2. Delegate to Compliance Agent
        comp_results = self.compliance_agent.check_compliance(fin_results, loan_amount)

        # 3. Handle Human-in-the-Loop Gate
        print(f"\n[ORCHESTRATOR: DECISION SYNTHESIS]")
        if comp_results["compliance_status"] == "NON_COMPLIANT":
            print(" [DECISION] LOAN AUTOMATICALLY REJECTED (Failed credit/DTI benchmarks).")
            return {"status": "REJECTED", "details": comp_results["reason"]}
        
        if comp_results["requires_human_approval"]:
            print(" [WARNING] HIGH VALUE TRANSACTION DETECTED ($100,000+ Threshold).")
            print(" [SUSPEND] WORKFLOW SUSPENDED: Emitting Event to Azure Service Bus / Durable Function...")
            print(" [NOTIFICATION] Notification pushed to Branch Vice President via Microsoft Teams Adaptive Card.")
            time.sleep(1)
            # Simulating human approval click
            human_decision = "APPROVED"  # Simulating VP clicking 'Approve'
            print(f" [SUCCESS] HUMAN APPROVAL RECEIVED: Branch VP stamped approval token.")
            print(f" [COMPLETE] FINAL STATUS: LOAN APPROVED & FUNDS DISBURSED FOR {fin_results['name']}!")
            return {"status": "APPROVED", "applicant": fin_results["name"], "approved_by": "VP_Risk_Management"}

if __name__ == "__main__":
    orchestrator = SupervisorOrchestrator()
    # Test high-value corporate loan scenario
    orchestrator.run_loan_approval_pipeline(user_id="USR-8921", loan_amount=250000.0)
