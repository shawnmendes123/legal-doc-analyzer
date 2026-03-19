import spacy
import pdfplumber
import re
import os

nlp = spacy.load("en_core_web_sm")

# Extract text
def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return None

    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

    return text

# 🔥 FIXED: Extract names (PERSON + ORG)
def extract_entities(text):
    doc = nlp(text)

    names = set()

    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            name = ent.text.strip()

            if "\n" in name:
                continue

            # Remove junk
            if "agreement" in name.lower():
                continue

            names.add(name)

    return {"names": list(names)}

# Extract clauses
def extract_clauses(text):
    return re.findall(r"(Clause\s\d+.*?)(?=Clause\s\d+|$)", text, re.DOTALL)

# Extract parties
def extract_parties_and_roles(text):
    clean_text = text.replace("\n", " ")

    intro_match = re.search(r'This.*?between(.*?)(Clause 1|WHEREAS)', clean_text, re.IGNORECASE)
    if not intro_match:
        return []

    intro_text = intro_match.group(1)

    pattern = r'([A-Za-z0-9 .,&]+?)\s*\(.*?"([^"]+)"\)'
    matches = re.findall(pattern, intro_text)

    parties = []

    for name, role in matches:
        name = re.sub(r'^(,?\s*and\s+)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^.*?between\s+', '', name, flags=re.IGNORECASE)
        name = name.strip(", ")

        if "agreement" in name.lower():
            continue

        if len(name) < 4:
            continue

        parties.append({
            "name": name,
            "role": role.strip()
        })

    return parties[:2]

# 🔥 FIXED: Temporal intelligence
def extract_temporal_data(text):
    clean_text = text.replace("\n", " ")

    # Exact dates
    exact_dates = re.findall(r'\d{1,2} \w+ \d{4}', clean_text)

    # ✅ FIX: full durations (number + unit)
    durations = re.findall(r'\b\d+\s+(?:working\s+)?(?:days?|weeks?|months?)\b', clean_text, re.IGNORECASE)

    # ✅ FIX: full year
    years = re.findall(r'\b(?:19|20)\d{2}\b', clean_text)

    return {
        "exact_dates": list(set(exact_dates)),
        "durations": list(set(durations)),
        "years": list(set(years))
    }

# Financials
def extract_financials(text):
    clean_text = text.replace("\n", " ")

    amount = re.search(r'₹\s?[\d,]+', clean_text)

    return {
        "amount": amount.group(0) if amount else "Not found"
    }

# MAIN
if __name__ == "__main__":
    file_path = input("Enter PDF path (or press Enter for default): ").strip('"')

    if file_path == "":
        file_path = "AGREEMENT.pdf"

    text = extract_text_from_pdf(file_path)

    if not text:
        exit()

    entities = extract_entities(text)
    clauses = extract_clauses(text)
    parties = extract_parties_and_roles(text)
    financials = extract_financials(text)
    temporal = extract_temporal_data(text)

    print("\n--- PARTIES ---")
    if len(parties) == 2:
        print(f"Party A: {parties[0]['name']} ({parties[0]['role']})")
        print(f"Party B: {parties[1]['name']} ({parties[1]['role']})")
    else:
        print("❌ Could not detect both parties.")

    print("\n--- ENTITIES ---")
    print("Names:", entities["names"])

    print("\n--- FINANCIALS ---")
    print("Amount:", financials["amount"])

    print("\n--- TIME ANALYSIS ---")
    print("Exact Dates:", temporal["exact_dates"])
    print("Durations:", temporal["durations"])
    print("Years:", temporal["years"])

    print("\n--- CLAUSES ---")
    for c in clauses:
        print(c[:200], "...\n")