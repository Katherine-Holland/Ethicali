import streamlit as st
import os
import sys
from dotenv import load_dotenv
import importlib.util
import traceback
import json  # ✅ for safe serialization

# --- Set up paths ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VALIDATOR_PATH = os.path.join(BASE_DIR, "backend", "validator")
if VALIDATOR_PATH not in sys.path:
    sys.path.append(VALIDATOR_PATH)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Load environment variables
load_dotenv()

# Framework options
FRAMEWORK_OPTIONS = {
    "EU AI Act": "eu_ai_act.validate_eu.validate_eu_framework",
}

# --- Streamlit UI ---
st.title("📂 Upload Your Dataset or Algorithm for Validation")
framework_choice = st.selectbox("Select a Compliance Framework", list(FRAMEWORK_OPTIONS.keys()))
uploaded_file = st.file_uploader(
    "Upload Dataset", 
    type=["csv", "xlsx", "json", "ipynb"]
)
algorithm_file = st.file_uploader(
    "Optional: Upload Algorithm", 
    type=["py", "yaml", "yml", "json", "ipynb"]
)


if (uploaded_file or algorithm_file) and framework_choice:
    with st.spinner("Running compliance validation..."):
        dataset_path = None
        algorithm_path = None
        os.makedirs("temp", exist_ok=True)

        if uploaded_file:
            dataset_path = os.path.join("temp", uploaded_file.name)
            with open(dataset_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                st.info(f"📊 Detected Dataset: {uploaded_file.name}")

        if algorithm_file:
            algorithm_path = os.path.join("temp", algorithm_file.name)
            with open(algorithm_path, "wb") as f:
                f.write(algorithm_file.getbuffer())
                st.info(f"⚙️ Detected Algorithm: {algorithm_file.name}")

        try:
            # Dynamic import
            framework_module_path = FRAMEWORK_OPTIONS[framework_choice]
            parts = framework_module_path.split(".")
            module_path = os.path.join(VALIDATOR_PATH, *parts[:-1]) + ".py"
            method_name = parts[-1]

            spec = importlib.util.spec_from_file_location("validate_module", module_path)
            validate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validate_module)

            validate_function = getattr(validate_module, method_name)
            result = validate_function(dataset_path=dataset_path, algorithm_path=algorithm_path)


            from backend.logging.audit_logger import save_audit_log
            save_audit_log(result, framework_choice, dataset_path, algorithm_path)

            st.success("✅ Validation Complete")
            for key, res in result.items():
                st.markdown(f"### {key.capitalize()}")
                try:
                    # ✅ Force safe JSON serialization
                    safe_res = json.loads(json.dumps(res, default=str))
                    st.json(safe_res)
                except Exception:
                    st.write(str(res))

        except Exception as e:
            st.error(f"⚠️ Validation failed for {framework_choice}: {str(e)}")
            debug_log_path = os.path.join(BASE_DIR, "backend", "logging", "debug.log")
            os.makedirs(os.path.dirname(debug_log_path), exist_ok=True)
            with open(debug_log_path, "a") as log:
                log.write("\n" + "-"*50 + "\n")
                log.write(traceback.format_exc())
                log.write("\n")

elif framework_choice:
    st.info("👆 Please upload either a dataset, an algorithm, or both.")
