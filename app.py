import streamlit as st
from google import genai
from google.genai import errors

# 1. Page Configuration & Styling
st.set_page_config(page_title="AI Logistics Auditor", page_icon="📦", layout="centered")
st.title("📦 AI Logistics Document Auditor")
st.write("Upload a Lorry Receipt, Bill of Lading, or Freight Invoice to instantly extract data and flag errors.")

# 2. Grab the hidden API key securely from Streamlit Secrets Management
try:
    YOUR_GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"].strip()
except Exception:
    YOUR_GEMINI_API_KEY = None

# Configure the updated SDK client layout
if YOUR_GEMINI_API_KEY:
    try:
        # The new SDK uses the standard client configuration layout
        client = genai.Client(api_key=YOUR_GEMINI_API_KEY)
    except Exception as config_err:
        st.error(f"Configuration initialization error: {config_err}")
        client = None

    if client:
        # 3. File Uploader Component
        uploaded_file = st.file_uploader("Upload Logistics Document (Text, PDF, or Image)", type=["txt", "pdf", "png", "jpg", "jpeg"])

        if uploaded_file is not None:
            with st.spinner("Processing document with AI..."):
                try:
                    # Read the file content text safely
                    bytes_data = uploaded_file.read()
                    document_text = bytes_data.decode("utf-8", errors="ignore")

                    # The exact auditing instruction template
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

                    # Generate content using the stable flash core engine model
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=ai_prompt,
                    )
                    
                    # 4. Display Results to the User
                    st.success("Audit Complete!")
                    st.subheader("📋 Extraction & Audit Report")
                    st.write(response.text)

                except errors.APIError as api_e:
                    st.error(f"Google API Error encountered: {api_e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred during processing: {e}")
else:
    st.error("Setup Incomplete: Please add the GEMINI_API_KEY to your Streamlit Cloud Secrets dashboard panel.")
