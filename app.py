import streamlit as st
import google.generativeai as genai

# 1. Page Configuration & Styling
st.set_page_config(page_title="AI Logistics Auditor", page_icon="📦", layout="centered")
st.title("📦 AI Logistics Document Auditor")
st.write("Upload a Bill of Lading, Freight Invoice, or Customs document to instantly extract data and flag errors.")

# 2. Get API Key securely from user or environment variables
api_key = st.text_input("Enter your Gemini API Key:", type="password", help="Get a free key from Google AI Studio")

if api_key:
    # Configure the Gemini AI engine
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")

    # 3. File Uploader Component
    uploaded_file = st.file_uploader("Upload Logistics Document (Text, PDF, or Image)", type=["txt", "pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        with st.spinner("Processing document with AI..."):
            try:
                # Read the file content
                bytes_data = uploaded_file.read()
                
                # Convert bytes to string for processing (assumes text/readable format)
                # For high-end PDFs/Images, Gemini can process bytes directly if structured correctly
                document_text = bytes_data.decode("utf-8", errors="ignore")

                # The exact prompt we instruct the AI to execute
                ai_prompt = f"""
                You are an expert logistics auditor. Analyze the following document text carefully.
                
                Extract the following details precisely in clean bullet points:
                1. Container Number (if visible)
                2. Total Freight Cost & Currency
                3. Origin Port / City
                4. Destination Port / City
                
                Compliance & Error Check:
                - Scan the document for missing mandatory fields (like signatures, weight, or dates).
                - Look for any glaring mismatches or potential compliance compliance risks.
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
    st.info("Please enter your Gemini API Key to activate the AI scanning tool.")
