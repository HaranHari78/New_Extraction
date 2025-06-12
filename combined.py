import os
import json
import re
from prompts_field import build_genetic_mutation_prompt, build_performance_status_prompt
from utils import load_config, call_openai_api

# --- CONFIG ---
input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\sentences"
mutation_output_file = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields\genetic_mutations_all.json"
performance_output_file = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields\performance_status_all.json"
os.makedirs(os.path.dirname(mutation_output_file), exist_ok=True)
os.makedirs(os.path.dirname(performance_output_file), exist_ok=True)

# BATCH RANGE – CHANGE for each batch
start_index = 0
end_index = 50

# --- LOAD CONFIG ---
config = load_config()
model = config['gpt_models']['model_gpt4o']

def clean_response(resp: str) -> str:
    return re.sub(r'```(?:json)?\n?|\n?```', '', resp).strip()

def load_existing_results(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

final_mutation_results = load_existing_results(mutation_output_file)
final_performance_results = load_existing_results(performance_output_file)

# --- Load files ---
all_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".json")])
batch_files = all_files[start_index:end_index]

for filename in batch_files:
    file_path = os.path.join(input_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        sentence_data = json.load(f)

    doc_title = sentence_data.get("document_title", filename.replace(".json", ""))

    # --- Mutation Extraction ---
    if not any(entry['genetic_mutations'][0]['docu_title'] == doc_title for entry in final_mutation_results):
        mutation_sents = sentence_data.get("genetic_mutations_sentences", [])
        if mutation_sents:
            text_block = " ".join(mutation_sents)
            prompt = build_genetic_mutation_prompt(text_block, doc_title)
            response = call_openai_api(prompt, model)
            if response:
                try:
                    raw = clean_response(response)
                    parsed = json.loads(raw)
                    if parsed.get("genetic_mutations"):
                        final_mutation_results.append(parsed)
                        print(f"✅ Mutation Extracted: {doc_title}")
                except Exception as e:
                    print(f"⚠️ Mutation Parse Error [{doc_title}]: {e}")

    # --- Performance Status Extraction ---
    if not any(entry['performance_status'][0]['docu_title'] == doc_title for entry in final_performance_results):
        perf_sents = sentence_data.get("performance_status_sentences", [])
        if perf_sents:
            text_block = " ".join(perf_sents)
            prompt = build_performance_status_prompt(text_block, doc_title)
            response = call_openai_api(prompt, model)
            if response:
                try:
                    raw = clean_response(response)
                    parsed = json.loads(raw)
                    if parsed.get("performance_status"):
                        final_performance_results.append(parsed)
                        print(f"✅ Performance Extracted: {doc_title}")
                except Exception as e:
                    print(f"⚠️ Performance Parse Error [{doc_title}]: {e}")

# --- Save Results ---
with open(mutation_output_file, 'w', encoding='utf-8') as f:
    json.dump(final_mutation_results, f, indent=4)

with open(performance_output_file, 'w', encoding='utf-8') as f:
    json.dump(final_performance_results, f, indent=4)

print(f"📦 Saved: {mutation_output_file} ({len(final_mutation_results)} mutation records)")
print(f"📦 Saved: {performance_output_file} ({len(final_performance_results)} performance records)")
