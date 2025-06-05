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

# Pattern to detect gene + mutation evidence
pattern = r"\b(NPM1|TP53|FLT3|ASXL1)\b.*?(mutated|wild[\s-]?type|positive|negative|not mutated)"

for idx, row in df.iterrows():
    title = row["title"]
    text = row["text"]

    if re.search(pattern, text, re.IGNORECASE):
        print(f"🔍 Found mutation pattern in: {title[:60]}...")

        prompt = mutation_extraction_prompt(text)
        response = call_openai_api(prompt, model)

        if not response:
            continue

        try:
            cleaned = re.sub(r'```(?:json)?\n?|\n?```', '', response).strip()
            data = json.loads(cleaned)
        except Exception as e:
            print(f"[⚠️ JSON Error] {title}: {e}")
            continue

        data["document_title"] = title
        results.append(data)

# Save output
os.makedirs("output", exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print(f"\n✅ Done. Results saved to {output_file} ({len(results)} patients)")
