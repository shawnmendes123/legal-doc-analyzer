import streamlit as st
import PyPDF2
import re
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Page config
st.set_page_config(page_title="Legal Analyzer", layout="centered")

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
st.title("⚖️ Legal Document Analyzer")
st.caption("Upload a legal document and extract key insights instantly")

# File upload
uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

# Extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# NLP Analysis
def analyze_text(text):
    doc = nlp(text)

    names = set()
    dates = set()
    amounts = set()

    for ent in doc.ents:

        # Extract Organizations / People
        if ent.label_ in ["ORG", "PERSON"]:
            # Filter meaningful names only
            if any(word in ent.text for word in ["Ltd", "Pvt", "LLP", "Company", "Group"]):
                names.add(ent.text)

        # Extract Dates
        elif ent.label_ == "DATE":
            dates.add(ent.text)

        # Extract Money
        elif ent.label_ == "MONEY":
            amounts.add(ent.text)

    return {
        "Names": list(names),
        "Dates": list(dates),
        "Amounts": list(amounts)
    }

# Run when file uploaded
if uploaded_file is not None:
    with st.spinner("Analyzing document..."):
        text = extract_text_from_pdf(uploaded_file)
        result = analyze_text(text)

    st.success("Analysis Complete ✅")

    # Layout in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👤 Parties / Organizations")
        if result["Names"]:
            for name in result["Names"]:
                st.write(f"- {name}")
        else:
            st.write("No valid entities found")

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