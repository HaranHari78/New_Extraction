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
