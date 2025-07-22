import streamlit as st
import os
import sys
from dotenv import load_dotenv
import importlib.util

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
    "EU AI Act": "eu_ai_act.validate_eu",  # relative to validator/
    # "California AI Law": "california.validate_california",
    # "ISO 42001": "iso_42001.validate_iso",
    # "NIST RMF": "nist_rmf.validate_nist",
    # "Texas AI Act": "texas.validate_texas"
}

# Streamlit UI
st.title("📂 Upload Your Dataset for Validation")
framework_choice = st.selectbox("Select a Compliance Framework", list(FRAMEWORK_OPTIONS.keys()))
uploaded_file = st.file_uploader("Upload Dataset (CSV)", type=["csv"])
algorithm_file = st.file_uploader("Optional: Upload Algorithm Script (Python)", type=["py"])

if uploaded_file and framework_choice:
    with st.spinner("Running compliance validation..."):

        # Save dataset temporarily
        dataset_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(dataset_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Save algorithm file temporarily if uploaded
        algorithm_path = None
        if algorithm_file:
            algorithm_path = os.path.join("temp", algorithm_file.name)
            with open(algorithm_path, "wb") as f:
                f.write(algorithm_file.getbuffer())

        # --- Dynamically import the validation module ---
        try:
            framework_module_path = FRAMEWORK_OPTIONS[framework_choice]
            module_parts = framework_module_path.split(".")
            module_file = os.path.join(VALIDATOR_PATH, *module_parts) + ".py"

            spec = importlib.util.spec_from_file_location("validate_module", module_file)
            validate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validate_module)

            # Run validation
            result = validate_module.validate_eu_framework(dataset_path, algorithm_path)

            st.success("✅ Validation Complete")
            for key, res in result.items():
                st.markdown(f"**{key.capitalize()}**")
                if isinstance(res, dict):
                    for k, v in res.items():
                        st.write(f"- {k}: {v}")
                else:
                    st.write(res)

        except Exception as e:
            st.error(f"⚠️ Validation failed for {framework_choice}.")
            st.exception(e)
