import json
import re
import os
import pandas as pd
from prompts import sentence_extraction_prompt, field_extraction_prompt
from utils import load_config, call_openai_api

# Configuration
openai_config = load_config()
model = openai_config['gpt_models']['model_gpt4o']
input_file = r"C:\Users\HariharaM12\Downloads\medicaldata.csv"
sentence_output_file = 'output/extracted_sentences.json'
structured_output_file = 'output/structured_data.json'
mutation_output_file = 'output/mutation_only_output.json'

sentence_results = []
structured_results = []
mutation_only_results = []

def clean_json_response(response: str):
    """Clean JSON response from OpenAI API"""
    if not response or not isinstance(response, str):
        return ""
    cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', response).strip()
    cleaned = cleaned.replace('\n', ' ')
    return cleaned

# Read input data
df = pd.read_csv(input_file, encoding='utf-8')

for index, row in df.iterrows():
    title = row.get('title', "")
    text = row.get('text', "")
    print(f"\n[Step 1] Analyzing Text: {title[:60]}...")

    if not text:
        continue

    # Step 1: Sentence Extraction
    prompt1 = sentence_extraction_prompt(title, text)
    extracted_sentences_json = call_openai_api(prompt1, model)
    print("[🔍 Raw API Response Snippet]", extracted_sentences_json[:300])

    if not extracted_sentences_json:
        continue

    cleaned_response = clean_json_response(extracted_sentences_json)
    try:
        extracted_sentences = json.loads(cleaned_response)
    except json.JSONDecodeError:
        print("[⚠️ JSON Error] Sentence extraction failed")
        continue

    sentence_results.append(extracted_sentences)

    # Step 2: Structured Extraction
    combined_text = ". ".join(
        extracted_sentences.get('aml_diagnosis_sentences', []) +
        extracted_sentences.get('precedent_disease_sentences', []) +
        extracted_sentences.get('performance_status_sentences', []) +
        extracted_sentences.get('mutational_status_sentences', [])
    )
    prompt2 = field_extraction_prompt(combined_text)
    structured_data_json = call_openai_api(prompt2, model)

    if not structured_data_json:
        continue

    cleaned_structured_data_json = clean_json_response(structured_data_json)
    try:
        structured_data = json.loads(cleaned_structured_data_json)
    except json.JSONDecodeError:
        print("[⚠️ JSON Error] Structured data parsing failed")
        continue

    structured_data["document_title"] = title
    structured_results.append(structured_data)

    # Extract mutation-only portion and save
    mutation_only_data = {
        "document_title": title,
        "mutational_status": structured_data.get("mutational_status", {})
    }
    mutation_only_results.append(mutation_only_data)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Save sentence output
try:
    with open(sentence_output_file, 'w', encoding='utf-8') as f:
        json.dump(sentence_results, f, indent=4)
    print(f"✅ Sentence results saved to: {sentence_output_file} ({len(sentence_results)} records)")
except Exception as e:
    print(f"❌ Failed to save sentence results: {e}")

# Save structured output
try:
    with open(structured_output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_results, f, indent=4)
    print(f"✅ Structured results saved to: {structured_output_file} ({len(structured_results)} records)")
except Exception as e:
    print(f"❌ Failed to save structured results: {e}")

# Save mutation-only output
try:
    with open(mutation_output_file, 'w', encoding='utf-8') as f:
        json.dump(mutation_only_results, f, indent=4)
    print(f"✅ Mutation-only results saved to: {mutation_output_file} ({len(mutation_only_results)} records)")
except Exception as e:
    print(f"❌ Failed to save mutation-only results: {e}")
