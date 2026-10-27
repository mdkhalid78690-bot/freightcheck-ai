import streamlit as st
from groq import Groq
import pypdf
import io

# 1. Page Configuration & Professional Styling
st.set_page_config(
    page_title="FreightCheck AI | Logistics Document Auditor", 
    page_icon="📦", 
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #0066cc;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 FreightCheck AI")
st.caption("Enterprise Logistics Document Auditor & Discrepancy Detection Engine (Powered by Groq High-Speed Inference)")

# 2. Secure API Key Retrieval
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"].strip()
except Exception:
    GROQ_API_KEY = None

SAMPLE_AUDIT_TEXT = """### 1. Document Classification & Key Extraction

* **Document Type:** Lorry Receipt / Consignment Note (Bilty)
* **Document Number & Date:** DEC-BLR-2026-88412 | 27-10-2026
* **Carrier / Transporter Name:** Deccan Express Logistics Pvt Ltd
* **Consignor (Sender):** Apex Industrial Tools Pvt Ltd (GSTIN: 29AABCA1234F1Z5) | Invoice: INV-45920 (Value: INR 8,45,000)
* **Consignee (Receiver):** Metro Hyper Retail Logistics Hub (GSTIN: 29XYZPA9876Q1Z2) | E-Way Bill: 531098234710 (Expiry: 28-10-2026)
* **Origin & Destination:** Peenya Industrial Area, Bengaluru, Karnataka ➔ Whitefield Warehouse Cluster, Bengaluru, Karnataka
* **Vehicle / Container / Seal Number:** Vehicle: KA-01-AG-4912 | Seal Number: SL-99214-B (Intact) | Driver: Ramesh Kumar (+91 98450 12345)
* **Weight & Volume (Gross / Net / Chargeable):** 
  * Declared Gross Cargo Weight (Invoice): 4,850 KG
  * Weighbridge Gross Weight (Laden Truck): 5,200 KG
  * Tare Weight (Truck): 3,200 KG
  * Actual Net Cargo Weight: 2,000 KG
  * Quantity / Package: 40 Wooden Crates
* **Total Freight Charges & Currency:** 
  * Total: INR 20,500
  * Base Freight: INR 18,500
  * Loading / Hamali: INR 1,200
  * Toll / Surcharge: INR 800
  * Detention / Demurrage: Not specified
  * Fuel Surcharge: Unitemized / absorbed in freight
  * GST / Taxes: Not explicitly itemized (RCM / Forward Charge status absent)
  * Terms: To Be Billed / Consignee Account

---

### 2. Discrepancy & Red Flag Audit

* **Mandatory Fields Check:** **[CLEAN]**
  * Consignor and Consignee GSTINs, addresses, invoice number, and e-way bill number with validity (valid through 28-10-2026 for intra-city transit) are present.
  * Transporter and driver authorization entries are acknowledged.

* **Calculations & Charge Verification:** **[WARNING]**
  * **Freight Charges:** The arithmetic sum of charges tallies correctly ($18,500 + 1,200 + 800 = INR 20,500). However, statutory Goods Transport Agency (GTA) GST compliance (whether billed at 5% RCM or 12% FCM) is not stated.
  * **Severe Weight & Discrepancy Calculation Error:** 
    * The weighbridge net weight is calculated as: 5,200 KG (Gross) - 3,200 KG (Tare) = 2,000 KG (Net).
    * The invoice declared cargo gross weight is **4,850 KG**, which indicates a shortfall of **2,850 KG** (over 58% missing weight).
    * The clerk's "Discrepancy Note" errantly compares the total laden vehicle weight (5,200 KG) to the declared invoice weight (4,850 KG) and states: *"Gross weight recorded exceeds declared invoice weight by 350 KG."* This conflates total vehicle weight with cargo payload, masking a massive physical shortage or an erroneous weighbridge tare entry.

* **Risk & Liability Warnings:** **[WARNING]**
  * **En-Route Regulatory Risk:** If intercepted by GST/RTO authorities, the drastic variance between the E-Way bill declared weight (4,850 KG) and physical net weight (2,000 KG) constitutes a major violation under Section 129 of the CGST Act, exposing the shipment to detention and penalties.
  * **Cargo Shortage / Theft Hazard:** If the vehicle is carrying only 2,000 KG across 40 crates, crates may be partially empty, or the weighbridge entry is incorrect.
  * **Omission of Detention Terms:** No terms are outlined for unloading detention at Whitefield Hub.

---

### 3. Executive Decision & Recommended Action

**Verdict:** **HOLD FOR REVIEW**

**Recommended Action for Dispatch / Billing Manager:**
1. **Immediate Vehicle Hold:** Halt dispatch/unloading immediately. Do not release the vehicle or accept the delivery based on this LR.
2. **Gross Re-Weighing:** Require KA-01-AG-4912 to undergo an immediate secondary weighbridge verification (Gross, Tare, Net) in the presence of an independent surveyor or warehouse supervisor.
3. **Crate Audit:** Inspect seal `SL-99214-B` and conduct a physical crate count and sample check across the 40 crates to determine whether cargo is missing or if the initial tare weight/gross weight was entered in error.
4. **Correct Bilty & E-Way Bill:** Cancel the current LR line item note. Once the true weight is established, issue an amended LR with corrected net cargo weight and explicitly note GTA GST treatment (e.g., *GST payable by Consignee under RCM*) before cargo handover."""

# 3. Main Workspace
col_upload, col_result = st.columns([1, 1], gap="medium")

with col_upload:
    st.subheader("1. Upload Document")
    uploaded_file = st.file_uploader(
        "Upload Lorry Receipt (LR), Bill of Lading (BL), or Freight Invoice",
        type=["pdf", "txt"]
    )
    
    st.markdown("---")
    st.markdown("**Quick Client Demo**")
    demo_button = st.button("⚡ Load Sample LR (Deccan Express)", use_container_width=True)

    if uploaded_file is not None:
        st.info(f"📄 File loaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

with col_result:
    st.subheader("2. Audit & Compliance Analysis")
    
    # CASE A: Demo Button Clicked (Zero API calls)
    if demo_button:
        st.success("✅ Sample LR Loaded: Deccan Express (DEC-BLR-2026-88412)")
        st.markdown(SAMPLE_AUDIT_TEXT)
        st.download_button(
            label="📥 Download Audit Summary (.txt)",
            data=SAMPLE_AUDIT_TEXT,
            file_name="FreightCheck_Audit_Sample_LR.txt",
            mime="text/plain",
            use_container_width=True
        )

    # CASE B: Custom File Uploaded
    elif uploaded_file is not None:
        audit_button = st.button("🔍 Run Full Logistics Audit", type="primary", use_container_width=True)
        
        if audit_button:
            if not GROQ_API_KEY:
                st.error("Setup Incomplete: Please add `GROQ_API_KEY` to your Streamlit Cloud Secrets dashboard.")
                st.stop()

            # Extract text safely from TXT or PDF
            try:
                uploaded_file.seek(0)
                extracted_text = ""
                if uploaded_file.name.lower().endswith(".pdf"):
                    pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() or ""
                else:
                    extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")
            except Exception as e:
                st.error(f"Error reading document: {e}")
                st.stop()

            if not extracted_text.strip():
                st.error("The uploaded document contains no readable text. Please try another file.")
                st.stop()

            ai_prompt = f"""You are an expert freight and logistics compliance auditor. Conduct a rigorous, forensic audit of the attached freight document text.

DOCUMENT CONTENT:
\"\"\"
{extracted_text}
\"\"\"

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

            with st.spinner("Connecting to Groq High-Speed Engine..."):
                try:
                    groq_client = Groq(api_key=GROQ_API_KEY)
                    stream = groq_client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[{"role": "user", "content": ai_prompt}],
                        temperature=0.1,
                        stream=True,
                    )

                    for chunk in stream:
                        content = chunk.choices[0].delta.content or ""
                        full_report += content
                        audit_container.markdown(full_report)

                    st.success("Audit Completed Successfully")
                    st.download_button(
                        label="📥 Download Audit Summary (.txt)",
                        data=full_report,
                        file_name=f"FreightCheck_Audit_{uploaded_file.name}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                except Exception as err:
                    st.error(f"Audit Engine Error: {err}")
    else:
        st.write("Upload a document on the left or click **'⚡ Load Sample LR'** to run an automated audit.")
        
