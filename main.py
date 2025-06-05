import json
import re
import os
import pandas as pd
from prompts import sentence_extraction_prompt, field_extraction_prompt
from utils import load_config, call_openai_api

# Print current working dir
print("📂 Current Working Directory:", os.getcwd())

# Ensure output folder exists
output_dir = r"C:\Users\HariharaM12\PycharmProjects\PythonProject\output"
os.makedirs(output_dir, exist_ok=True)

# File paths
sentence_output_file = os.path.join(output_dir, 'extracted_sentences.json')
structured_output_file = os.path.join(output_dir, 'structured_data.json')

# Load config
openai_config = load_config()
model = openai_config['gpt_models']['model_gpt4o']
input_file = r"C:\Users\HariharaM12\Downloads\medicaldata.csv"

# Output lists
sentence_results = []
structured_results = []

def clean_json_response(response: str):
    """Clean JSON response from OpenAI API"""
    if not response or not isinstance(response, str):
        return ""
    cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', response).strip()
    cleaned = cleaned.replace('\n', ' ')
    return cleaned

# Load data
df = pd.read_csv(input_file, encoding='utf-8')
print(f"📄 Total rows to process: {len(df)}")

# Loop through records
for index, row in df.iterrows():
    title = row.get('title', "")
    text = row.get('text', "")
    print(f"\n🔄 Processing: {title[:60]}")

    if not text:
        continue

    # Step 1: Extract relevant sentences
    prompt1 = sentence_extraction_prompt(title, text)
    extracted_sentences_json = call_openai_api(prompt1, model)

    if not extracted_sentences_json:
        print("⚠️ Empty sentence extraction response")
        continue

    cleaned_response = clean_json_response(extracted_sentences_json)
    try:
        extracted_sentences = json.loads(cleaned_response)
    except json.JSONDecodeError:
        print("⚠️ JSON decoding failed for sentence extraction")
        continue

    sentence_results.append(extracted_sentences)

    # Step 2: Use extracted sentences to get structured data
    combined_text = ". ".join(
        extracted_sentences.get('aml_diagnosis_sentences', []) +
        extracted_sentences.get('precedent_disease_sentences', []) +
        extracted_sentences.get('performance_status_sentences', []) +
        extracted_sentences.get('mutational_status_sentences', [])
    )
    prompt2 = field_extraction_prompt(combined_text)
    structured_data_json = call_openai_api(prompt2, model)

    if not structured_data_json:
        print("⚠️ Empty structured data response")
        continue

    cleaned_structured_data_json = clean_json_response(structured_data_json)
    try:
        structured_data = json.loads(cleaned_structured_data_json)
    except json.JSONDecodeError:
        print("⚠️ JSON decoding failed for structured data")
        continue

    structured_data["document_title"] = title
    structured_results.append(structured_data)

# ✅ Save sentence output
try:
    with open(sentence_output_file, 'w', encoding='utf-8') as f:
        json.dump(sentence_results, f, indent=4)
    print(f"✅ Sentence results saved: {sentence_output_file} ({len(sentence_results)} records)")
except Exception as e:
    print(f"❌ Failed to save sentence results: {e}")

# ✅ Save structured output
try:
    with open(structured_output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_results, f, indent=4)
    print(f"✅ Structured results saved: {structured_output_file} ({len(structured_results)} records)")
except Exception as e:
    print(f"❌ Failed to save structured results: {e}")
