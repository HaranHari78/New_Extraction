def build_sentence_prompt(text: str) -> str:
    return f"""
You are analyzing a clinical note for an AML cancer patient.

Extract and return only the sentences (verbatim from the text) that provide information for each of the following medical categories:

1. AML Diagnosis
2. Precedent Disease (any prior cancer or comorbidity with date if present)
3. Performance Status (ECOG or KPS, including scores or descriptions)
4. Mutational Status (NPM1, RUNX1, TP53, FLT3, ASXL1, or others)
5. Treatment Plans (e.g. chemotherapy, aza/ven, radiation, induction therapy)
6. Hospitalization Reasons (symptoms or causes for admission like fever, fatigue)
7. Lab Results (e.g. creatinine, WBC count, blasts %, etc.)
8. Genetic Mutations (including IDH1, DNMT3A, NRAS, etc.)
9. Discharge or Follow-up Plans (e.g. aftercare, coordination of care)
10. General Diagnosis Summary (summarized diagnostic statements)

Here is the clinical text:
\"\"\"{text}\"\"\"

Return JSON format only:
{{
  "aml_diagnosis_sentences": [],
  "precedent_disease_sentences": [],
  "performance_status_sentences": [],
  "mutational_status_sentences": [],
  "treatment_sentences": [],
  "hospitalization_reason_sentences": [],
  "lab_result_sentences": [],
  "genetic_mutations_sentences": [],
  "admission_discharge_plan_sentences": [],
  "diagnosis_summary_sentences": []
}}
"""
