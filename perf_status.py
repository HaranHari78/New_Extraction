import os
import json
import re
from prompts_field import build_performance_status_prompt
from utils import load_config, call_openai_api

# --- CONFIG ---
input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\sentences"
output_file = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields\performance_status_all.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# BATCH RANGE – CHANGE HERE for each run
start_index = 0
end_index = 50

# --- LOAD CONFIG ---
config = load_config()
model = config['gpt_models']['model_gpt4o']

# --- CLEAN RESPONSE ---
def clean_response(resp: str) -> str:
    return re.sub(r'```(?:json)?\n?|\n?```', '', resp).strip()

# Load existing results (to prevent overwriting)
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        final_results = json.load(f)
else:
    final_results = []

# Load batch files
all_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".json")])
batch_files = all_files[start_index:end_index]

for filename in batch_files:
    file_path = os.path.join(input_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        sentence_data = json.load(f)

    doc_title = sentence_data.get("document_title", filename.replace(".json", ""))

    # Skip if already processed
    if any(entry['performance_status'][0]['docu_title'] == doc_title for entry in final_results):
        print(f"⏭️ Already processed: {doc_title}")
        continue

    perf_sents = sentence_data.get("performance_status_sentences", [])
    if not perf_sents:
        continue

    text_block = " ".join(perf_sents)
    prompt = build_performance_status_prompt(text_block, doc_title)
    response = call_openai_api(prompt, model)

    if not response:
        print(f"❌ No response for: {doc_title}")
        continue

    try:
        raw = clean_response(response)
        parsed = json.loads(raw)

        if parsed.get("performance_status"):
            final_results.append(parsed)
            print(f"✅ Done: {doc_title}")

    except Exception as e:
        print(f"⚠️ Error parsing {doc_title}: {e}")

# Save combined result
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_results, f, indent=4)

print(f"\n📦 Saved: {output_file} ({len(final_results)} records)")
