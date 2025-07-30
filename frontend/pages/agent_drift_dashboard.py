import streamlit as st
import sys
import os
import json
import datetime
from difflib import SequenceMatcher
import traceback

# === Paths ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

BACKEND_PATH = os.path.join(BASE_DIR, "backend")
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

VALIDATOR_PATH = os.path.join(BACKEND_PATH, "validator")
os.makedirs(VALIDATOR_PATH, exist_ok=True)

DRIFT_LOG_DIR = os.path.join(BASE_DIR, "backend", "logging", "agent_drift_logs")
os.makedirs(DRIFT_LOG_DIR, exist_ok=True)

# === Drift Utils ===
def load_all_audits():
    audits = []
    for f in sorted(os.listdir(DRIFT_LOG_DIR)):
        if f.endswith(".json"):
            path = os.path.join(DRIFT_LOG_DIR, f)
            with open(path, "r") as file:
                data = json.load(file)
            audits.append({"file": f, "data": data})
    return audits

def calc_drift_score(conv_a, conv_b):
    text_a = " ".join([c["agent"] for c in conv_a])
    text_b = " ".join([c["agent"] for c in conv_b])
    similarity = SequenceMatcher(None, text_a, text_b).ratio()
    return round((1 - similarity) * 100, 2)

def calc_compliance_score(audit_data):
    if "results" not in audit_data:
        return None
    results = audit_data["results"]
    total_checks = len(results)
    passed = sum(1 for v in results.values() if v["status"] == "Yes")
    return round((passed / total_checks) * 100, 2) if total_checks > 0 else None

# === UI ===
st.title("🤖 AI Agent Audit & Drift Dashboard")

# === Upload & Audit ===
st.subheader("Upload AI Agent Conversation Log (JSON)")
agent_file = st.file_uploader("Upload", type=["json"])

if agent_file:
    try:
        with st.spinner("Running AI Agent Audit..."):
            os.makedirs("temp", exist_ok=True)
            agent_log_path = os.path.join("temp", agent_file.name)
            with open(agent_log_path, "wb") as f:
                f.write(agent_file.getbuffer())

            with open(agent_log_path, "r") as f:
                conversation = json.load(f)

            # ✅ Dynamic import of EU Agent Validator
            from backend.validator.eu_ai_act import validate_agent_framework
            result = validate_agent_framework.validate_eu_agent(conversation)

            # ✅ Save to drift logs
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            drift_log_file = os.path.join(DRIFT_LOG_DIR, f"agent_audit_{timestamp}.json")
            with open(drift_log_file, "w") as f:
                json.dump(result, f, indent=2)

            st.success("✅ AI Agent Audit Complete")

            # === Compliance Display ===
            agent_data = result.get("agent_analysis", result)
            if "results" in agent_data:
                audit_results = agent_data["results"]
                st.subheader("AI Agent Compliance Report")

                for category, data in audit_results.items():
                    status = data["status"]
                    color = "green" if status == "Yes" else "red" if status == "No" else "orange"
                    st.markdown(f"#### <span style='color:{color}'>{category.upper()}: {status}</span>", unsafe_allow_html=True)
                    st.write(data["details"])

                    if data.get("examples") and status != "Yes":
                        st.markdown("**⚠️ Example(s) that failed:**")
                        for ex in data["examples"]:
                            st.write(f"👤 **User:** {ex.get('user')}")
                            st.write(f"🤖 **Agent:** {ex.get('agent')}")
                            st.markdown("---")

                    if data.get("eu_ai_act_articles"):
                        st.markdown("**📜 Related EU AI Act Articles:**")
                        for art in data["eu_ai_act_articles"]:
                            st.markdown(f"- {art}")

    except Exception as e:
        st.error(f"⚠️ Agent Audit failed: {str(e)}")
        debug_log_path = os.path.join(BASE_DIR, "backend", "logging", "debug.log")
        os.makedirs(os.path.dirname(debug_log_path), exist_ok=True)
        with open(debug_log_path, "a") as log:
            log.write("\n" + "-"*50 + "\n")
            log.write(traceback.format_exc())
            log.write("\n")

# === Drift & Compliance Monitoring ===
st.subheader("📈 Drift & Compliance Over Time")

audits = load_all_audits()

if len(audits) < 2:
    st.info("Run at least 2 audits to see drift trends.")
else:
    # ✅ Drift score calculation
    scores = []
    timestamps = []
    for i in range(1, len(audits)):
        prev = audits[i-1]["data"]
        curr = audits[i]["data"]

        if "conversation" in prev and "conversation" in curr:
            score = calc_drift_score(prev["conversation"], curr["conversation"])
            scores.append(score)
            ts = audits[i]["file"].replace("agent_audit_", "").replace(".json", "")
            timestamps.append(ts)

    if scores:
        drift_chart_data = [
            {"Timestamp": ts, "Drift Score (%)": score}
            for ts, score in zip(timestamps, scores)
        ]
        st.line_chart(drift_chart_data)

    # ✅ Compliance trend calculation
    compliance_scores = []
    compliance_timestamps = []
    for a in audits:
        cs = calc_compliance_score(a["data"])
        if cs is not None:
            compliance_scores.append(cs)
            compliance_timestamps.append(a["file"].replace("agent_audit_", "").replace(".json", ""))

    if compliance_scores:
        compliance_chart_data = [
            {"Timestamp": ts, "Compliance (%)": cs}
            for ts, cs in zip(compliance_timestamps, compliance_scores)
        ]
        st.line_chart(compliance_chart_data)

# === Historical Table ===
if len(audits) > 0:
    st.subheader("📜 Historical Audit Logs")

    history_rows = []
    prev_conv = None
    for audit in audits:
        timestamp = audit["file"].replace("agent_audit_", "").replace(".json", "")
        compliance = calc_compliance_score(audit["data"])
        overall_status = audit["data"].get("overall_compliance", "N/A")
        drift = None
        if prev_conv and "conversation" in audit["data"]:
            drift = calc_drift_score(prev_conv, audit["data"]["conversation"])
        prev_conv = audit["data"].get("conversation", [])

        history_rows.append({
            "Timestamp": timestamp,
            "Overall Compliance": overall_status,
            "Compliance %": compliance if compliance is not None else "N/A",
            "Drift vs Previous": drift if drift is not None else "N/A"
        })

    st.table(history_rows)
