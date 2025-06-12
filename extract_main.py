import json
import re
import os
import pandas as pd
from mutation_prompt import mutation_extraction_prompt
from utils import load_config, call_openai_api

# Config
openai_config = load_config()
model = openai_config['gpt_models']['model_gpt4o']
input_file = r"C:\Users\HariharaM12\Downloads\medicaldata.csv"
output_file = "output/mutational_status_only.json"
results = []

# Load CSV
df = pd.read_csv(input_file, encoding='utf-8')

# Define pattern to check if patient note contains mutation-related content
pattern = r"\b(NPM1|TP53|FLT3|ASXL1)\b.*?(mutated|wild[\s-]?type|positive|negative|not mutated)"

# Process each record
for idx, row in df.iterrows():
    title = row["title"]
    text = row["text"]

    if not re.search(pattern, text, re.IGNORECASE):
        continue

    print(f"🔍 Found mutation pattern in: {title[:60]}...")

    # Pass index and title as ID + Name
    prompt = mutation_extraction_prompt(text=text, patient_id=idx, name=title)
    response = call_openai_api(prompt, model)

    if not response:
        print("⚠️ Empty response from API")
        continue

    try:
        cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', response).strip()
        data = json.loads(cleaned)
    except Exception as e:
        print(f"[⚠️ JSON Error] {title}: {e}")
        continue

    results.append(data)

# Save mutation-only output
os.makedirs("output", exist_ok=True)
try:
    with open(output_file, 'w', encoding='utf-8') as f:

        json.dump(results, f, indent=4)
    print(f"\n✅ Mutation-only results saved to: {output_file} ({len(results)} records)")
except Exception as e:
    print(f"❌ Failed to save mutation results: {e}")


output:

[
    {
        "document_title": "bfad7df253_44215_ Unmapped_b847916fd5",
        "mutational_status": {
            "NPM1": {
                "status": "mutated",
                "date": "2021-01-04",
                "evidence": "BMBx on 1/4 showed AML with monocytic differentiation (73% blasts) and he was subsequently started on aza/ven on 1/5. Prelim cytogenetic analysis is normal w/ molectular profile demonstrating DNMT3A R882C 44%, IDH1 R132G 41%, NPM1 Type A mutation 40%, NRAS G13R 40%."
            },
            "TP53": {
                "status": "",
                "date": "",
                "evidence": ""
            },
            "FLT3": {
                "status": "",
                "date": "",
                "evidence": ""
            },
            "ASXL1": {
                "status": "",
                "date": "",
                "evidence": ""
            }
        }
    },


# field_extraction_main.py

import os
import json
import re
from prompts_field import build_mutation_prompt
from utils import load_config, call_openai_api

# --- CONFIG ---
input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\sentences"
output_file = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields\mutational_status_all.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# BATCH RANGE – CHANGE HERE for each run
start_index = 0
end_index = 50

# --- LOAD CONFIG ---
config = load_config()
model = config['gpt_models']['model_gpt4o']

# --- HELPERS ---
def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def clean_response(resp: str) -> str:
    return re.sub(r'```(?:json)?\n?|\n?```', '', resp).strip()

# Load existing results (for appending)
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        final_results = json.load(f)
else:
    final_results = []

# List of all files and slice for batch
all_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".json")])
batch_files = all_files[start_index:end_index]

for filename in batch_files:
    file_path = os.path.join(input_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        sentence_data = json.load(f)

    doc_title = sentence_data.get("document_title", filename.replace(".json", ""))
    
    # Skip if this doc already exists in output
    if any(doc["document_title"] == doc_title for doc in final_results):
        print(f"⏭️ Already processed: {doc_title}")
        continue

    mutation_sents = sentence_data.get("mutational_status_sentences", [])
    if not mutation_sents:
        continue

    prompt = build_mutation_prompt(mutation_sents, doc_title)
    response = call_openai_api(prompt, model)

    if not response:
        print(f"❌ No response for: {doc_title}")
        continue

    try:
        raw = clean_response(response)
        parsed = json.loads(raw)
        filtered_genes = {
            gene: data for gene, data in parsed.get("mutational_status", {}).items()
            if any(data.values())
        }
        if not filtered_genes:
            continue

        final_results.append({
            "document_title": doc_title,
            "mutational_status": filtered_genes
        })
        print(f"✅ Done: {doc_title}")

    except Exception as e:
        print(f"⚠️ Error parsing {doc_title}: {e}")

# Save updated results
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_results, f, indent=4)

print(f"\n📦 Updated output saved to {output_file} ({len(final_results)} total records)")
