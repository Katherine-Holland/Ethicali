import os
import sys
import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
import hashlib

# Add blockchain path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.blockchain.scripts.blockchain_manager import BlockchainManager
from backend.models.bias_detection import BiasDetectionNode
from backend.models.transparency_checker import TransparencyNode
from backend.models.accountability_checker import AccountabilityNode
from backend.models.fairness_checker import FairnessNode

# Company Details
COMPANY_NAME = "ETHICALI"
COMPANY_LOGO = "/workspace/ethicaliai/ethicali.png"
EU_AI_ACT_URL = "https://artificialintelligenceact.eu"

# Initialize Nodes
bias_node = BiasDetectionNode({"Gender": 0.3, "Age_Group": 0.1, "Region": 0.2})
transparency_node = TransparencyNode(["Gender", "Age_Group", "Region"])
accountability_node = AccountabilityNode(["timestamp", "version", "decision_log"])
fairness_node = FairnessNode({"Gender": 0.25, "Age_Group": 0.15, "Region": 0.2})

# Initialize Blockchain Manager
abi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/blockchain/abi/contract_abi.json"))

blockchain_manager = BlockchainManager(
    provider_url="https://eth-sepolia.g.alchemy.com/v2/REDACTED_ALCHEMY_KEY_2",
    contract_address="0x36C479454CD9394c6940ff91dF998f6BEB1b3752",
    abi_path=abi_path
)

# Generate PDF
class CompliancePDF(FPDF):
    def header(self):
        if os.path.exists(COMPANY_LOGO):
            self.image(COMPANY_LOGO, 10, 8, 33)
        self.set_font("Arial", size=16)
        self.cell(0, 10, f"{COMPANY_NAME} Compliance Report", border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.cell(0, 10, f"Page {self.page_no()} - {COMPANY_NAME}", align="C")

def generate_pdf(compliance_summary, mitigation_details, uploaded_docs, transaction_hash, additional_hash):
    pdf = CompliancePDF()
    pdf.set_font("Arial", size=12)
    pdf.add_page()

    pdf.cell(0, 10, "Compliance Report Overview", ln=True, align="C")
    pdf.ln(10)
    
    pdf.multi_cell(0, 10, f"Compliance Summary:\n{compliance_summary}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Mitigation Details:\n{mitigation_details}")

    pdf.ln(5)
    pdf.cell(0, 10, f"Transaction Hash: {transaction_hash}", ln=True)
    pdf.cell(0, 10, f"Additional Security Hash: {additional_hash}", ln=True)

    if uploaded_docs:
        pdf.ln(5)
        pdf.cell(0, 10, "Supporting Documents:", ln=True)
        for doc in uploaded_docs:
            pdf.cell(0, 10, f"- {doc}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, f"For further details on compliance regulations, visit: {EU_AI_ACT_URL}")

    file_path = "compliance_report.pdf"
    pdf.output(file_path)
    return file_path


def generate_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def display_results(results, section_title, node_type, explanation):
    color_map = {"bias": "#ffe6e6", "transparency": "#e6f7ff", "accountability": "#e6ffe6", "fairness": "#fff4e6"}
    background_color = color_map.get(node_type, "#ffffff")

    compliant = results.get("compliant")
    st.markdown(
        f"""
        <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <h4>{section_title}</h4>
            <p><strong>What this does:</strong> {explanation}</p>
            <p><strong>Overall Compliance:</strong> {'✅ Pass' if compliant else '❌ Fail'}</p>
        </div>
        """, unsafe_allow_html=True
    )

    if "features" in results:
        for feature, details in results["features"].items():
            st.markdown(f"- **{feature}**: {details.get('reason', 'No reason provided')}")

def main():
    st.title("AI Validator Node: Blockchain-Integrated Validation")

    with st.sidebar:
        st.header("Compliance Framework Selection")
        selected_framework = st.radio("Choose the Framework:", ["EU AI Act", "California Laws"])

        st.header("Blockchain Actions")

        st.subheader("Upload Compliance Report")
        metadata = st.text_area(
            "Enter Metadata Notes for Compliance Report:",
            placeholder="Add details such as reviewer names, version history, or additional context.",
            key="metadata"
        )
        if st.button("Upload Compliance Report"):
            try:
                description = f"Compliance report for {selected_framework}"
                mitigation_details = st.session_state.get("mitigation_details", "No mitigation details provided.")
                uploaded_docs = st.session_state.get("uploaded_docs", [])

                compliance_report_content = f"{description}{mitigation_details}{[doc.name for doc in uploaded_docs]}"
                hash_value = generate_hash(compliance_report_content)

                record_id = blockchain_manager.upload_compliance_summary(
                    description, hash_value, metadata
                )

                st.session_state["transaction_hash"] = hash_value

                etherscan_url = f"https://sepolia.etherscan.io/tx/{hash_value}"
                st.markdown(f"[View transaction on Etherscan]({etherscan_url})")
                st.success(f"Compliance report uploaded successfully with hash: {hash_value}")
            except Exception as e:
                st.error(f"Error uploading report: {e}")

    tab1, tab2, tab3, tab4 = st.tabs(["Upload Dataset", "Upload Algorithm", "Mitigations", "Download Report"])

    with tab1:
        dataset_file = st.file_uploader("Upload your dataset (CSV):", type=["csv"], key="dataset")
        if dataset_file:
            dataset = pd.read_csv(dataset_file)
            st.write("### Preview of Dataset")
            st.dataframe(dataset)

            # Evaluate dataset
            bias_results = bias_node.evaluate_dataset(dataset)
            fairness_results = fairness_node.evaluate_dataset(dataset)
            transparency_results = transparency_node.evaluate_dataset(dataset)
            accountability_results = accountability_node.evaluate_dataset(dataset)

            dataset_analysis_results = {
                "Bias": bias_results,
                "Fairness": fairness_results,
                "Transparency": transparency_results,
                "Accountability": accountability_results
            }
            
            # Store results in session state without displaying them
            st.session_state["dataset_analysis"] = dataset_analysis_results

            st.success("Dataset analysis results saved successfully!")

            # Displaying detailed results with color coding
            for key, result in dataset_analysis_results.items():
                compliant = result.get("compliant")
                color = "#e6ffe6" if compliant else "#ffe6e6"

                st.markdown(
                    f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                    <h4>{key} Analysis</h4>
                    <p><strong>Overall Compliance:</strong> {'✅ Pass' if compliant else '❌ Fail'}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

                if "features" in result and result["features"]:
                    st.markdown("**Detailed Explanation:**")
                    for feature, details in result["features"].items():
                        reason = details.get("reason", "No details available")
                        st.markdown(f"- **{feature}**: {reason}")
                else:
                    st.warning(f"No detailed reasons available for {key}")

            st.success("Dataset analysis results saved successfully!")


    with tab2:
        algorithm_file = st.file_uploader("Upload your algorithm (JSON):", type=["json"], key="algorithm")
        if algorithm_file:
            algorithm = json.load(algorithm_file)
            st.write("### Preview of Algorithm")
            st.json(algorithm)

            transparency_results = transparency_node.evaluate_algorithm(algorithm)
            accountability_results = accountability_node.evaluate_algorithm(algorithm)

            algorithm_analysis_results = {
                "Transparency": transparency_results,
                "Accountability": accountability_results
            }

            st.session_state["algorithm_analysis"] = algorithm_analysis_results

            # Displaying detailed results with color coding
            for key, result in algorithm_analysis_results.items():
                compliant = result.get("compliant")
                color = "#e6ffe6" if compliant else "#ffe6e6"

                st.markdown(
                    f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                        <h4>{key} Analysis</h4>
                        <p><strong>Overall Compliance:</strong> {'✅ Pass' if compliant else '❌ Fail'}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

                if "features" in result and result["features"]:
                    st.markdown("**Detailed Explanation:**")
                    for feature, details in result["features"].items():
                        reason = details.get("reason", "No details available")
                        st.markdown(f"- **{feature}**: {reason}")
                else:
                    st.warning(f"No detailed reasons available for {key}")

            st.success("Algorithm analysis results saved successfully!")


    with tab3:
        st.write("Mitigations and Risk Management")
        st.text_area("Describe your mitigation strategies and risk management efforts.", key="mitigation_details")
        st.file_uploader("Upload additional supporting documentation (PDF/DOCX):", type=["pdf", "docx"],
                         accept_multiple_files=True, key="uploaded_docs")

        with tab4:
            st.subheader("Compliance Report Preview")

            # EU AI Act Overview
            st.markdown('<p class="report-header">Understanding the EU AI Act</p>', unsafe_allow_html=True)
            st.info(
                """
                The **EU AI Act** ensures transparency, fairness, and accountability 
                in AI systems, mitigating risks and ensuring ethical AI deployment. 
                Compliance helps align with legal standards and build trust with stakeholders.  
                [Learn more](https://artificialintelligenceact.eu)
                """
            )

            # Overall Compliance Summary Section
            st.markdown("### Dataset Analysis Results")
            if "dataset_analysis" in st.session_state:
                overall_dataset_compliance = all(result.get("compliant") for result in st.session_state["dataset_analysis"].values())
                st.markdown(
                    f"""
                    <div style="background-color: {'#2ECC71' if overall_dataset_compliance else '#E74C3C'}; 
                                padding: 6px; border-radius: 8px; text-align: center; 
                                color: white; font-weight: bold; width: 50%; margin: 0 auto;">
                        Dataset Compliance: {'✅ Pass' if overall_dataset_compliance else '❌ Fail'}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Detailed breakdown in collapsible sections
                for key, result in st.session_state["dataset_analysis"].items():
                    with st.expander(f"{key} Compliance Details"):
                        compliant = result.get("compliant")
                        color = "#2ECC71" if compliant else "#E74C3C"

                        st.markdown(
                            f"""
                            <div style="background-color: {color}; padding: 4px; 
                                        border-radius: 4px; margin-bottom: 3px; 
                                        color: white; width: 60%; margin: 0 auto;
                                        font-size: 14px;">
                                <h5 style="margin: 5px 0; font-size: 16px;">{key} Compliance Check</h5>
                                <p style="margin: 3px 0;"><strong>Status:</strong> {'✅ Pass' if compliant else '❌ Fail'}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if key == "Accountability":
                            if not compliant:
                                st.markdown("**Missing Metadata Keys:**")
                                missing_metadata = result.get("missing_metadata", [])
                                if missing_metadata:
                                    st.markdown(f"- {', '.join(missing_metadata)}")
                                st.markdown(f"**Reason:** {result.get('reason', 'No reason provided')}")
                            else:
                                st.success("All accountability metadata is correctly recorded.")

                        elif "features" in result and result["features"]:
                            st.markdown("**Detailed Insights:**")
                            for feature, details in result["features"].items():
                                reason = details.get("reason", "No details available")
                                threshold = details.get("threshold", "N/A")
                                actual_value = details.get("actual_value", "N/A")

                                st.markdown(f"- **{feature}:** {reason}")
                                st.markdown(f"  - **Threshold:** {threshold}")
                                st.markdown(f"  - **Actual Value:** {actual_value}")
            else:
                st.warning("No dataset analysis results available.")

            # Algorithm Analysis Section (Corrected indentation)
            st.markdown("### Algorithm Analysis Results")
            if "algorithm_analysis" in st.session_state:
                overall_algorithm_compliance = all(result.get("compliant") for result in st.session_state["algorithm_analysis"].values())
                st.markdown(
                    f"""
                    <div style="background-color: {'#2ECC71' if overall_algorithm_compliance else '#E74C3C'}; 
                                padding: 6px; border-radius: 8px; text-align: center; 
                                color: white; font-weight: bold; width: 50%; margin: 0 auto;">
                        Algorithm Compliance: {'✅ Pass' if overall_algorithm_compliance else '❌ Fail'}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Detailed breakdown in collapsible sections
                for key, result in st.session_state["algorithm_analysis"].items():
                    with st.expander(f"{key} Compliance Details"):
                        compliant = result.get("compliant")
                        color = "#2ECC71" if compliant else "#E74C3C"

                        st.markdown(
                            f"""
                            <div style="background-color: {color}; padding: 4px; 
                                        border-radius: 4px; margin-bottom: 3px; 
                                        color: white; width: 60%; margin: 0 auto;
                                        font-size: 14px;">
                                <h5 style="margin: 5px 0; font-size: 16px;">{key} Compliance Check</h5>
                                <p style="margin: 3px 0;"><strong>Status:</strong> {'✅ Pass' if compliant else '❌ Fail'}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if key == "Transparency":
                            if not compliant:
                                st.markdown("**Missing Keys:**")
                                st.markdown(f"- {', '.join(result.get('missing_keys', []))}")
                                st.markdown(f"**Reason:** {result.get('reason', 'No details available')}")
                            else:
                                st.success("Algorithm meets all transparency requirements.")

                        elif key == "Accountability":
                            if not compliant:
                                missing_keys = result.get("missing_keys", [])
                                if missing_keys:
                                    st.markdown("**Missing Metadata Keys:**")
                                    st.markdown(f"- {', '.join(missing_keys)}")
                                st.markdown(f"**Reason:** {result.get('reason', 'No reason provided')}")
                            else:
                                st.success("All accountability metadata is correctly recorded.")
            else:
                st.warning("No algorithm analysis results available.")

            # Mitigation Details Section
            st.markdown("### Mitigation Details")
            mitigation_details = st.session_state.get("mitigation_details", "No mitigation details provided.")
            st.info(mitigation_details)

            uploaded_docs = st.session_state.get("uploaded_docs", [])
            if uploaded_docs:
                st.markdown("#### Uploaded Supporting Documents")
                for doc in uploaded_docs:
                    st.markdown(f"- {doc.name}")

            # PDF Download Button
            if st.button("Download Compliance Report"):
                compliance_summary = "Compliance report including dataset and algorithm analysis."
                transaction_hash = st.session_state.get("transaction_hash", "N/A")
                additional_hash = st.session_state.get("additional_hash", "N/A")

                pdf_path = generate_pdf(compliance_summary, mitigation_details, uploaded_docs, transaction_hash, additional_hash)

                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Compliance Report PDF",
                        data=pdf_file,
                        file_name="compliance_report.pdf",
                        mime="application/pdf"
                    )

                    if key == "Transparency":
                        if not compliant:
                            st.markdown("**Missing Keys:**")
                            st.markdown(f"- {', '.join(result.get('missing_keys', []))}")
                        st.markdown(f"**Reason:** {result.get('reason', 'No details available')}")

                    elif key == "Accountability":
                        if not compliant:
                            missing_keys = result.get("missing_keys", [])
                            if missing_keys:
                                st.markdown("**Missing Metadata Keys:**")
                                st.markdown(f"- {', '.join(missing_keys)}")
                            st.markdown(f"**Reason:** {result.get('reason', 'No reason provided')}")


if __name__ == "__main__":
    main()