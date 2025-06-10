import json
import re
import os
import pandas as pd
from prompts import sentence_extraction_prompt, field_extraction_prompt
from utils import load_config, call_openai_api

# Ensure output folder exists
output_dir = r"C:\Users\HariharaM12\PycharmProjects\Medical_Data\output"
os.makedirs(output_dir, exist_ok=True)

# File paths
sentence_output_file = os.path.join(output_dir, 'extracted_sentences.json')
structured_output_file = os.path.join(output_dir, 'structured_data.json')

# Config
openai_config = load_config()
model = openai_config['gpt_models']['model_gpt4o']
input_file = r"C:\Users\HariharaM12\Downloads\medicaldata.csv"

# Results
sentence_results = []
structured_results = []

def clean_json_response(response: str):
    if not response or not isinstance(response, str):
        return ""
    cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', response).strip()
    cleaned = cleaned.replace('\n', ' ')
    return cleaned

# Read input CSV
df = pd.read_csv(input_file, encoding='utf-8')
print(f"\U0001F4C4 Total rows: {len(df)}")

# Process rows
for index, row in df.iterrows():
    text = row.get('text', "")
    patient_id = index
    print(f"\n\U0001F501 Processing row: {index}")

    if not text:
        continue

    # Step 1: Sentence extraction
    prompt1 = sentence_extraction_prompt(text)
    extracted_sentences_raw = call_openai_api(prompt1, model)

    if not extracted_sentences_raw:
        print("⚠️ Sentence extraction failed")
        continue

    cleaned_sentences = clean_json_response(extracted_sentences_raw)
    try:
        extracted_sentences = json.loads(cleaned_sentences)
        extracted_sentences["patient_id"] = patient_id
        sentence_results.append(extracted_sentences)
    except json.JSONDecodeError:
        print("⚠️ Sentence JSON parse error")
        continue

    # Step 2: Field extraction
    combined_text = ". ".join(
        extracted_sentences.get('aml_diagnosis_sentences', []) +
        extracted_sentences.get('precedent_disease_sentences', []) +
        extracted_sentences.get('performance_status_sentences', []) +
        extracted_sentences.get('mutational_status_sentences', [])
    )

    prompt2 = field_extraction_prompt(combined_text)
    structured_raw = call_openai_api(prompt2, model)

    if not structured_raw:
        print("⚠️ Structured extraction failed")
        continue

    cleaned_structured = clean_json_response(structured_raw)
    try:
        structured_data = json.loads(cleaned_structured)
        structured_data["patient_id"] = patient_id
        structured_results.append(structured_data)
    except json.JSONDecodeError:
        print("⚠️ Structured JSON parse error")
        continue

# ✅ Save outputs
try:
    with open(sentence_output_file, 'w', encoding='utf-8') as f:
        json.dump(sentence_results, f, indent=4)
    print(f"✅ Saved sentence results → {sentence_output_file}")
except Exception as e:
    print(f"❌ Error saving sentence file: {e}")

try:
    with open(structured_output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_results, f, indent=4)
    print(f"✅ Saved structured results → {structured_output_file}")
except Exception as e:
    print(f"❌ Error saving structured file: {e}")
