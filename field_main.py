import os
import json
import re
from prompts_field import build_field_prompt
from utils import load_config, call_openai_api

# Input: sentence files
sentence_input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\sentences"
# Output: structured fields per title
field_output_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields"
os.makedirs(field_output_dir, exist_ok=True)

# Load config and model
config = load_config()
model_name = config['gpt_models']['model_gpt4o']

# Clean response
def sanitize_json_response(raw_response: str):
    if not raw_response or not isinstance(raw_response, str):
        return ""
    cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', raw_response).strip()
    return cleaned.replace('\n', ' ')

# Clean filename for saving
def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# Loop through each sentence file
for filename in os.listdir(sentence_input_dir):
    if not filename.endswith(".json"):
        continue

    input_path = os.path.join(sentence_input_dir, filename)

    with open(input_path, 'r', encoding='utf-8') as f:
        sentence_data = json.load(f)

    # Combine all sentence categories
    combined_sentences = []
    for key in [
        "aml_diagnosis_sentences",
        "precedent_disease_sentences",
        "performance_status_sentences",
        "mutational_status_sentences",
        "treatment_sentences",
        "hospitalization_reason_sentences",
        "lab_result_sentences",
        "genetic_mutations_sentences",
        "admission_discharge_plan_sentences",
        "diagnosis_summary_sentences"
    ]:
        combined_sentences.extend(sentence_data.get(key, []))

    combined_text = ". ".join(combined_sentences)

    if not combined_text.strip():
        print(f"Skipping empty combined text: {filename}")
        continue

    # Build and call prompt
    prompt = build_field_prompt(combined_text)
    response = call_openai_api(prompt, model_name)

    if not response:
        print(f" No response from API for {filename}")
        continue

    cleaned_response = sanitize_json_response(response)

    try:
        field_data = json.loads(cleaned_response)
        field_data["document_title"] = sentence_data.get("document_title", filename.replace(".json", ""))
    except json.JSONDecodeError:
        print(f" JSON parse error for: {filename}")
        continue

    # Save structured output per title
    output_filename = sanitize_filename(field_data["document_title"]) + ".json"
    output_path = os.path.join(field_output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(field_data, f, indent=4)

    print(f" Saved → {output_path}")

next 50:

import os
import json
import re
from prompts_field import build_field_prompt
from utils import load_config, call_openai_api

# Input: sentence files
sentence_input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\sentences"
# Output: structured fields per title
field_output_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields"
os.makedirs(field_output_dir, exist_ok=True)

# Load config and model
config = load_config()
model_name = config['gpt_models']['model_gpt4o']

# Clean response
def sanitize_json_response(raw_response: str):
    if not raw_response or not isinstance(raw_response, str):
        return ""
    cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', raw_response).strip()
    return cleaned.replace('\n', ' ')

# Clean filename for saving
def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# Loop through each sentence file
for filename in os.listdir(sentence_input_dir):
    if not filename.endswith(".json"):
        continue

    input_path = os.path.join(sentence_input_dir, filename)

    with open(input_path, 'r', encoding='utf-8') as f:
        sentence_data = json.load(f)

    # Combine all sentence categories
    combined_sentences = []
    for key in [
        "aml_diagnosis_sentences",
        "precedent_disease_sentences",
        "performance_status_sentences",
        "mutational_status_sentences",
        "treatment_sentences",
        "hospitalization_reason_sentences",
        "lab_result_sentences",
        "genetic_mutations_sentences",
        "admission_discharge_plan_sentences",
        "diagnosis_summary_sentences"
    ]:
        combined_sentences.extend(sentence_data.get(key, []))

    combined_text = ". ".join(combined_sentences)

    if not combined_text.strip():
        print(f"Skipping empty combined text: {filename}")
        continue

    # Build and call prompt
    prompt = build_field_prompt(combined_text)
    response = call_openai_api(prompt, model_name)

    if not response:
        print(f" No response from API for {filename}")
        continue

    cleaned_response = sanitize_json_response(response)

    try:
        field_data = json.loads(cleaned_response)
        field_data["document_title"] = sentence_data.get("document_title", filename.replace(".json", ""))
    except json.JSONDecodeError:
        print(f" JSON parse error for: {filename}")
        continue

    # Ensure unique output file using sentence filename (minus .json)
    input_filename_no_ext = os.path.splitext(filename)[0]
    output_filename = sanitize_filename(f"{field_data['document_title']}_{input_filename_no_ext}") + ".json"
    output_path = os.path.join(field_output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(field_data, f, indent=4)

    print(f" Saved → {output_path}")

