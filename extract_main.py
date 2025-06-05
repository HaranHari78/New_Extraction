import json
import re
import os
import pandas as pd
from mutation_prompt import mutation_extraction_prompt
from utils import load_config, call_openai_api

# Configuration
openai_config = load_config()
model = openai_config['gpt_models']['model_gpt4o']
input_file = r"C:\Users\HariharaM12\Downloads\medicaldata.csv"  # Update if needed
output_file = "output/mutational_status_only.json"
results = []

# Load input CSV
df = pd.read_csv(input_file, encoding='utf-8')

# Define pattern to check if patient note contains mutation-related content
pattern = r"\b(NPM1|TP53|FLT3|ASXL1)\b.*?(mutated|wild[\s-]?type|positive|negative|not mutated)"

# Process each record
for idx, row in df.iterrows():
    title = row["title"]
    text = row["text"]

    # Skip rows that don't mention any of the mutation genes with possible mutation status
    if not re.search(pattern, text, re.IGNORECASE):
        continue

    print(f"🔍 Found mutation pattern in: {title[:60]}...")

    # Prepare and call prompt
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

# Save mutation-only output
os.makedirs("output", exist_ok=True)
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print(f"\n✅ Mutation-only results saved to: {output_file} ({len(results)} records)")
except Exception as e:
    print(f"❌ Failed to save mutation results: {e}")
