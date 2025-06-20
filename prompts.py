def sentence_extraction_prompt(title, text):
    return f"""
    You are analyzing a clinical document for an AML cancer patient.
    Extract all sentences that contain potential evidence for the following categories:
    1. AML Diagnosis Date
    2. Precedent Disease (with the date of mention)
    3. Performance Status at Baseline:
        - ECOG score (0-4)
        - Karnofsky score (KPS)
        - With associated dates
    4. Mutational Status (with gene name + value + date if available):
        - NPM1, RUNX1, TP53, FLT3, ASXL1

    Document Title: {title}
    Document Text:
    {text}

    Return a JSON like:
    {{
        "document_title": "{title}",
        "aml_diagnosis_sentences": [],
        "precedent_disease_sentences": [],
        "performance_status_sentences": [],
        "mutational_status_sentences": []
    }}
    """

def field_extraction_prompt(text: str):
    return f"""
Extract the following information from the clinical note provided below. Return output in JSON format only.

Clinical Note:
\"\"\"{text}\"\"\"

Extract and return this information:
1. AML Diagnosis Date — mm/dd/yyyy format, and sentence
2. Precedent Disease — a list of objects:
  - disease name
  - date of mention
  - sentence
3. Performance Status:
  - ECOG score
  - ECOG date
  - ECOG sentence
  - KPS score
  - KPS date
  - KPS sentence
4. Mutational Status — for each of the genes NPM1, RUNX1, TP53, FLT3, ASXL1:
  - status (e.g., mutated, wild type)
  - date of finding (if any)
  - sentence

Return JSON in this structure:
{{
  "document_title": "",
  "aml_diagnosis_date": {{
    "value": "",
    "evidence": ""
  }},
  "precedent_disease": [
    {{
      "name": "",
      "date": "",
      "evidence": ""
    }}
  ],
  "performance_status": {{
    "ecog_score": {{
      "value": "",
      "date": "",
      "evidence": ""
    }},
    "kps_score": {{
      "value": "",
      "date": "",
      "evidence": ""
    }}
  }},
  "mutational_status": {{
    "NPM1": {{"status": "", "date": "", "evidence": ""}},
    "RUNX1": {{"status": "", "date": "", "evidence": ""}},
    "TP53": {{"status": "", "date": "", "evidence": ""}},
    "FLT3": {{"status": "", "date": "", "evidence": ""}},
    "ASXL1": {{"status": "", "date": "", "evidence": ""}}
  }}
}}
"""

