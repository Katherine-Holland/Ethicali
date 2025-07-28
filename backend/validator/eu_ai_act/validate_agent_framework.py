import json
import os
from validator.eu_ai_act.eu_agent_node import validate_agent

def validate_eu_agent(agent_log_path):
    """Validate AI agent conversation log (file path or direct list)."""

    # ✅ Allow direct list or JSON file path
    if isinstance(agent_log_path, list):
        conversation = agent_log_path
    else:
        if not agent_log_path or not os.path.exists(agent_log_path):
            return {
                "status": "error",
                "message": "Agent log file not found or invalid path"
            }

        try:
            with open(agent_log_path, "r", encoding="utf-8") as f:
                conversation = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load agent log: {str(e)}"
            }

    # ✅ Pass to the core agent validator
    return validate_agent(conversation)
