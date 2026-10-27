from google import genai
from google.genai import errors
from google.genai import types
import streamlit as st

# 1. Page Configuration & Professional Styling
st.set_page_config(
    page_title="FreightCheck AI | Logistics Document Auditor",
    page_icon="📦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #0066cc;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📦 FreightCheck AI")
st.caption(
    "Enterprise Logistics Document Auditor & Discrepancy Detection Engine"
)

# 2. Secure API Key Retrieval
try:
  YOUR_GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"].strip()
except Exception:
  YOUR_GEMINI_API_KEY = None

if not YOUR_GEMINI_API_KEY:
  st.error(
      "Setup Incomplete: Please add `GEMINI_API_KEY` to your Streamlit Cloud"
      " Secrets dashboard."
  )
  st.stop()

try:
  client = genai.Client(api_key=YOUR_GEMINI_API_KEY)
except Exception as config_err:
  st.error(f"Client initialization error: {config_err}")
  st.stop()

# 3. Main Workspace
col_upload, col_result = st.columns([1, 1], gap="medium")

with col_upload:
  st.subheader("1. Upload Document")
  uploaded_file = st.file_uploader(
      "Upload Lorry Receipt (LR), Bill of Lading (BL), or Freight Invoice",
      type=["pdf", "png", "jpg", "jpeg", "txt"],
  )

  if uploaded_file is not None:
    if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
      st.image(
          uploaded_file,
          caption="Uploaded Document Preview",
          use_container_width=True,
      )
    else:
      st.info(
          f"📄 File loaded: **{uploaded_file.name}**"
          f" ({uploaded_file.size / 1024:.1f} KB)"
      )

with col_result:
  st.subheader("2. Audit & Compliance Analysis")

  if uploaded_file is not None:
    audit_button = st.button(
        "🔍 Run Full Logistics Audit", type="primary", use_container_width=True
    )

    if audit_button:
      # Reset file pointer to prevent empty 0-byte reads
      uploaded_file.seek(0)
      bytes_data = uploaded_file.read()

      mime_type = uploaded_file.type
      if not mime_type:
        if uploaded_file.name.lower().endswith(".pdf"):
          mime_type = "application/pdf"
        elif uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
          mime_type = "image/jpeg"
        else:
          mime_type = "text/plain"

      if (
          mime_type == "text/plain"
          or uploaded_file.name.lower().endswith(".txt")
      ):
        text_str = bytes_data.decode("utf-8", errors="ignore")
        document_payload = (
            f"--- ATTACHED FREIGHT DOCUMENT CONTENT ---\n{text_str}"
        )
      else:
        document_payload = types.Part.from_bytes(
            data=bytes_data, mime_type=mime_type
        )

      ai_prompt = """
You are an expert freight and logistics compliance auditor. Conduct a rigorous, forensic audit of the attached document.

Structure your response strictly using these Markdown sections:

### 1. Document Classification & Key Extraction
- **Document Type:** (e.g., Lorry Receipt / Bilty, Bill of Lading, Freight Tax Invoice, Delivery Challan)
- **Document Number & Date:** 
- **Carrier / Transporter Name:** 
- **Consignor (Sender):** 
- **Consignee (Receiver):** 
- **Origin & Destination:** 
- **Vehicle / Container / Seal Number:** 
- **Weight & Volume (Gross / Net / Chargeable):** 
- **Total Freight Charges & Currency:** (Explicitly list freight rate, detention/demurrage terms, fuel surcharge, GST/taxes if present)

### 2. Discrepancy & Red Flag Audit
Scan every field and mark status clearly with [CLEAN] or [WARNING]:
- **Mandatory Fields Check:** (Are dates, authorized signatures, company stamps, and consignment numbers present?)
- **Calculations & Charge Verification:** (Do the weight, unit rate, and total line items tally without arithmetic error?)
- **Risk & Liability Warnings:** (Check for missing driver signatures, absent seal numbers, damaged goods remarks, or vague delivery terms)

### 3. Executive Decision & Recommended Action
Provide a clear verdict: **APPROVED**, **HOLD FOR REVIEW**, or **REJECTED**, followed by the exact operational next step for the dispatch/billing manager.
"""

      audit_container = st.empty()
      full_report = ""

      with st.spinner("Connecting to FreightCheck Audit Engine..."):
        try:
          # Stream the response live to avoid read timeouts
          response_stream = client.models.generate_content_stream(
              model="gemini-3.8-flash",
              contents=[document_payload, ai_prompt],
              config=types.GenerateContentConfig(
                  thinking_config=types.ThinkingConfig(thinking_budget=0),
                  temperature=0.1,
              ),
          )

          for chunk in response_stream:
            if chunk.text:
              full_report += chunk.text
              audit_container.markdown(full_report)

          st.success("Audit Completed Successfully")

          st.download_button(
              label="📥 Download Audit Summary (.txt)",
              data=full_report,
              file_name=f"FreightCheck_Audit_{uploaded_file.name}.txt",
              mime="text/plain",
              use_container_width=True,
          )

        except errors.APIError as api_err:
          if "503" in str(api_err):
            st.warning(
                "⚡ Google API capacity surge detected. Please wait 10 seconds"
                " and click retry."
            )
          else:
            st.error(f"Gemini API Error: {api_err}")
        except Exception as err:
          st.error(f"Processing Error: {err}")
  else:
    st.write("Upload a document on the left to begin the automated audit.")
