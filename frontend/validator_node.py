import streamlit as st
import pandas as pd
import json
from bias_detection_node import BiasDetectionNode
from transparency_node import TransparencyNode
from accountability_node import AccountabilityNode
from fairness_node import FairnessNode

# Initialize Nodes
bias_node = BiasDetectionNode({
    "Gender": 0.3,
    "Age_Group": 0.1,
    "Region": 0.2,
})
transparency_node = TransparencyNode(["Gender", "Age_Group", "Region"])
accountability_node = AccountabilityNode(["timestamp", "version", "decision_log"])
fairness_node = FairnessNode({
    "Gender": 0.25,
    "Age_Group": 0.15,
    "Region": 0.2,
})

def display_results(results, section_title, node_type, explanation):
    """
    Display validation results with detailed insights, explanations, and color-coded sections.
    """
    color_map = {
        "bias": "#ffe6e6",         # Light red for Bias Validation
        "transparency": "#e6f7ff", # Light blue for Transparency Validation
        "accountability": "#e6ffe6", # Light green for Accountability Validation
        "fairness": "#fff4e6",     # Light orange for Fairness Validation
    }
    background_color = color_map.get(node_type, "#ffffff")

    compliant = results.get("compliant")
    st.markdown(
        f"""
        <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <h4 style="margin-bottom: 10px;">{section_title}</h4>
            <p><strong>What this does:</strong> {explanation}</p>
            <p><strong>Overall Compliance:</strong> {'✅ Pass' if compliant else '❌ Fail'}</p>
        </div>
        """, unsafe_allow_html=True
    )

    if "features" in results:
        for feature, details in results["features"].items():
            reason = details.get("reason", "No reason provided")
            st.markdown(f"- **{feature}**: {reason}")
            below_threshold = details.get("below_threshold", {})
            if below_threshold:
                st.markdown(f"   - Below threshold for: {', '.join(below_threshold.keys())}")
    if "missing_metadata" in results:
        st.markdown(f"**Missing Metadata:** {', '.join(results['missing_metadata'])}")
    if "missing_keys" in results:
        st.markdown(f"**Missing Keys:** {', '.join(results['missing_keys'])}")
    if "reason" in results:
        st.markdown(f"**Reason:** {results['reason']}")

def compliance_reminder():
    """
    Display a detailed compliance reminder for optional areas.
    """
    st.markdown(
        """
        ---
        ### Compliance Reminder
        **Important Notes:**
        - **Bias**: Ensure your dataset and algorithm meet fairness thresholds to avoid discriminatory outcomes.
        - **Fairness**: Verify balanced representation across categories such as gender, age, or region.
        - **Transparency**: Ensure all required fields and metadata are present for traceability and governance.
        - **Accountability**: Maintain accurate records such as timestamps, versions, and decision logs for auditability.
        - While mitigation plans are not validated directly within datasets or algorithms, conducting regular audits and maintaining external risk assessment reports can significantly enhance compliance and risk mitigation efforts.
        ---
        """
    )

def main():
    st.title("AI Validator Node: Simplified Validation")

    selected_framework = st.sidebar.selectbox(
        "Choose the AI Act or Framework:",
        options=["EU AI Act", "California Laws"]
    )

    tab1, tab2 = st.tabs(["Upload Dataset", "Upload Algorithm"])

    with tab1:
        st.header("Dataset Validation")
        dataset_file = st.file_uploader("Upload your dataset (CSV):", type=["csv"])
        if dataset_file:
            dataset = pd.read_csv(dataset_file)
            st.write("Preview of Dataset:")
            st.dataframe(dataset)

            bias_results = bias_node.evaluate_dataset(dataset)
            display_results(
                bias_results, 
                "Dataset Bias Validation", 
                "bias", 
                "The Bias Detection Node checks if your dataset treats all groups fairly. It identifies underrepresentation or bias to prevent discrimination."
            )

            fairness_results = fairness_node.evaluate_dataset(dataset)
            display_results(
                fairness_results, 
                "Dataset Fairness Validation", 
                "fairness", 
                "The Fairness Node ensures that all groups in your dataset are equally and appropriately represented."
            )

            transparency_results = transparency_node.evaluate_dataset(dataset)
            display_results(
                transparency_results, 
                "Dataset Transparency Validation", 
                "transparency", 
                "The Transparency Node ensures that all required fields are present in your dataset, supporting traceability."
            )

            accountability_results = accountability_node.evaluate_dataset(dataset)
            display_results(
                accountability_results, 
                "Dataset Accountability Validation", 
                "accountability", 
                "The Accountability Node verifies that your dataset contains accurate records, such as timestamps and decision logs, to ensure auditability."
            )

            compliance_reminder()

    with tab2:
        st.header("Algorithm Validation")
        algorithm_file = st.file_uploader("Upload your algorithm (JSON):", type=["json"])
        if algorithm_file:
            algorithm = json.load(algorithm_file)
            st.write("Preview of Algorithm:")
            st.json(algorithm)

            transparency_results = transparency_node.evaluate_algorithm(algorithm)
            display_results(
                transparency_results, 
                "Algorithm Transparency Validation", 
                "transparency", 
                "The Transparency Node checks that all required metadata keys in your algorithm are present and complete."
            )

            accountability_results = accountability_node.evaluate_algorithm(algorithm)
            display_results(
                accountability_results, 
                "Algorithm Accountability Validation", 
                "accountability", 
                "The Accountability Node ensures your algorithm maintains key records like versioning and decision logs for traceability."
            )

            compliance_reminder()

if __name__ == "__main__":
    main()
