import json
import os
from validator.eu_ai_act.eu_agent_node import validate_agent

def validate_eu_agent(agent_log_path):
    """Validate AI agent conversation log (file path or direct list)."""

    # ✅ Allow direct list input or JSON file path
    if isinstance(agent_log_path, list):
        conversation = agent_log_path
    else:
        if not agent_log_path or not os.path.exists(agent_log_path):
            return {
                "agent_analysis": {
                    "status": "error",
                    "message": "Agent log file not found or invalid path"
                }
            }

        try:
            with open(agent_log_path, "r", encoding="utf-8") as f:
                conversation = json.load(f)
        except Exception as e:
            return {
                "agent_analysis": {
                    "status": "error",
                    "message": f"Failed to load agent log: {str(e)}"
                }
            }

    # ✅ Schema validation: expect list of dicts with role/content
    if not isinstance(conversation, list) or not all(isinstance(c, dict) for c in conversation):
        return {
            "agent_analysis": {
                "status": "error",
                "message": "Invalid agent log format. Expected a list of conversation dicts."
            }
        }

    # ✅ Pass to core agent validator and wrap in consistent format
    core_results = validate_agent(conversation)

    return {
        "agent_analysis": core_results
    }
