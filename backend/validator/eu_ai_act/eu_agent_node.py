import json
from validator.agent_validator import run_agent_validation

EU_ARTICLE_MAP = {
    "bias": ["Article 10 - Data & Data Governance", "Article 5 - Prohibited Practices"],
    "explainability": ["Article 13 - Transparency", "Article 14 - Human Oversight"],
    "consistency": ["Article 9 - Risk Management", "Article 15 - Accuracy & Robustness"]
}

def validate_agent(conversation_input):
    """Validate AI agent conversation log from JSON file path or direct list."""
    try:
        # ✅ Handle both file path and direct list
        if isinstance(conversation_input, list):
            conversation = conversation_input
        else:
            with open(conversation_input, "r") as f:
                conversation = json.load(f)

        base_results = run_agent_validation(conversation) or {}

        compliance_report = {}
        overall_pass = True

        for category, result in base_results.items():
            if category == "overall_compliance":
                continue

            status = result.get("result", "No")
            compliance_report[category] = {
                "status": status,
                "details": result.get("details", {}),
                "examples": result.get("examples", []),
                "eu_ai_act_articles": EU_ARTICLE_MAP.get(category, [])
            }

            if status != "Yes":
                overall_pass = False

        return {
            "status": "complete",
            "overall_compliance": "Yes" if overall_pass else "No",
            "results": compliance_report,
            "conversation_length": len(conversation)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Agent validation failed: {str(e)}"
        }
