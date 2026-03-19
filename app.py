import streamlit as st
import PyPDF2
import re

# Page config
st.set_page_config(page_title="ShawnLex", layout="centered")

# Styling
st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
            color: white;
        }
        .stButton>button {
            border-radius: 10px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("⚖️ ShawnLex")
st.caption("AI-powered legal document analyzer")

# Upload
uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

# Extract text
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# Analyze text (NO spaCy — deploy safe)
def analyze_text(text):
    names = set()
    dates = set()
    amounts = set()

    # Company names (better pattern)
    company_pattern = r'([A-Z][A-Za-z&., ]+(?:Pvt\. Ltd\.|Ltd\.|LLP|Group|Company))'
    matches = re.findall(company_pattern, text)

    for match in matches:
        names.add(match.strip())

    # Dates
    date_pattern = r'\d{1,2} \w+ \d{4}'
    dates.update(re.findall(date_pattern, text))

    # Amounts
    amount_pattern = r'₹\d+(?:,\d+)*'
    amounts.update(re.findall(amount_pattern, text))

    return {
        "Names": list(names),
        "Dates": list(dates),
        "Amounts": list(amounts)
    }

# Run analysis
if uploaded_file is not None:
    with st.spinner("Analyzing document..."):
        text = extract_text_from_pdf(uploaded_file)
        result = analyze_text(text)

    st.success("Analysis Complete ✅")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👤 Parties")
        if result["Names"]:
            for name in result["Names"]:
                st.write(f"- {name}")
        else:
            st.write("No parties found")

    with col2:
        st.subheader("📅 Dates")
        if result["Dates"]:
            for date in result["Dates"]:
                st.write(f"- {date}")
        else:
            st.write("No dates found")

    with col3:
        st.subheader("💰 Amounts")
        if result["Amounts"]:
            for amount in result["Amounts"]:
                st.write(f"- {amount}")
        else:
            st.write("No amounts found")

else:
    st.info("Upload a PDF to begin analysis")