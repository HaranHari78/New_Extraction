def sentence_extraction_prompt(text: str):
    return f"""
You are analyzing a clinical document for an AML cancer patient.
Extract all sentences that contain potential evidence for:
1. AML Diagnosis Date
2. Precedent Disease (with date)
3. Performance Status (ECOG/KPS with dates)
4. Mutational Status (NPM1, RUNX1, TP53, FLT3, ASXL1)

Text:
{text}

Return JSON like:
{{
  "aml_diagnosis_sentences": [],
  "precedent_disease_sentences": [],
  "performance_status_sentences": [],
  "mutational_status_sentences": []
}}
"""

def field_extraction_prompt(text: str):
    return f"""
Extract the following from the clinical note below. Return JSON only.

Note:
"""{text}"""

Return:
{{
  "aml_diagnosis_date": {{"value": "", "evidence": ""}},
  "precedent_disease": [{{"name": "", "date": "", "evidence": ""}}],
  "performance_status": {{
    "ecog_score": {{"value": "", "date": "", "evidence": ""}},
    "kps_score": {{"value": "", "date": "", "evidence": ""}}
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
