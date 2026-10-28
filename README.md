# 📦 FreightCheck AI — Enterprise Logistics Document Auditor

An automated forensic auditing engine that parses freight documents (Lorry Receipts, Bills of Lading, and Invoices) to catch billing leaks, weight shortages, and regulatory violations in under 1 second.

🔗 **Live Application:** https://freightcheck-ai.streamlit.app/

---

## ⚡ Key Capabilities
- **Payload Variance Detection:** Automatically compares weighbridge net weight against declared gross cargo weight to flag missing goods.
- **GST & Interstate Compliance:** Validates proper tax classification (IGST vs. CGST/SGST) based on origin and destination state codes.
- **E-Way Bill Validation:** Verifies validity dates against consignment dispatch dates to prevent Section 129 highway seizures.
- **Arithmetic Integrity:** Audits base freight, loading (Hamali), fuel surcharges, and detention fees against invoice subtotals.
- **Actionable Verdicts:** Provides instant operational decisions: `APPROVED`, `HOLD FOR REVIEW`, or `REJECTED`.

---

## 🛠️ Tech Stack
- **Frontend / Cloud:** Streamlit Cloud
- **Inference Engine:** Groq Cloud (`openai/gpt-oss-120b`)
- **Document Processing:** PyPDF & Python
