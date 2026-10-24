import streamlit as st
import google.generativeai as genai

# 1. HARDCODE YOUR FREE API KEY HERE SO CUSTOMERS DON'T SEE IT
# Replace the text below with your actual long Gemini API key (e.g., "AIzaSy...")
YOUR_GEMINI_API_KEY = AQ.Ab8RN6J_2GzPQlgFQwQnsXUhV0irBMPnDkQWZkLW298Bqumx1Q

# 2. Page Configuration & Styling
st.set_page_config(page_title="AI Logistics Auditor", page_icon="📦", layout="centered")
st.title("📦 AI Logistics Document Auditor")
st.write("Upload a Lorry Receipt, Bill of Lading, or Freight Invoice to instantly extract data and flag errors.")

# Configure the Gemini AI engine automatically in the background
if YOUR_GEMINI_API_KEY and YOUR_GEMINI_API_KEY != "PASTE_YOUR_ACTUAL_GEMINI_API_KEY_HERE":
    genai.configure(api_key=YOUR_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # 3. File Uploader Component
    uploaded_file = st.file_uploader("Upload Logistics Document (Text, PDF, or Image)", type=["txt", "pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        with st.spinner("Processing document with AI..."):
            try:
                # Read the file content
                bytes_data = uploaded_file.read()
                document_text = bytes_data.decode("utf-8", errors="ignore")

                # The exact prompt we instruct the AI to execute
                ai_prompt = f"""
                You are an expert logistics auditor. Analyze the following document text carefully.
                
                Extract the following details precisely in clean bullet points:
                1. Container/Vehicle Number (if visible)
                2. Total Freight Cost & Currency
                3. Origin Port / City
                4. Destination Port / City
                
                Compliance & Error Check:
                - Scan the document for missing mandatory fields (like signatures, weight, dates, or seals).
                - Look for any glaring mismatches or potential compliance risks.
                - Flag anything suspicious as a warning.
                
                Document Content:
                {document_text}
                """

                # Generate the audit response
                response = model.generate_content(ai_prompt)
                
                # 4. Display Results to the User
                st.success("Audit Complete!")
                st.subheader("📋 Extraction & Audit Report")
                st.write(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.error("Developer Setup Missing: Please paste your Gemini API Key inside the app.py code.")
