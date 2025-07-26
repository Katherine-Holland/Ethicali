import json
from backend.validator.eu_ai_act.eu_agent_node import validate_agent

def validate_eu_agent(agent_log_path):
    """Validate AI agent conversation log (file path or direct list)."""
    if isinstance(agent_log_path, list):
        conversation = agent_log_path
    else:
        with open(agent_log_path, "r") as f:
            conversation = json.load(f)

    return validate_agent(conversation)
