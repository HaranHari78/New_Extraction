import os
import json
from pathlib import Path

# Folder containing field-level JSON files
input_dir = Path(r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields")
output_file = Path(r"C:\Users\HariharaM12\PycharmProjects\New_project\output\mutational_status_combined.json")

# List to hold results
all_mutation_data = []

# Loop through files
for filename in os.listdir(input_dir):
    if not filename.endswith(".json"):
        continue

    path = input_dir / filename
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    doc_title = data.get("document_title", filename.replace(".json", ""))
    mutation_block = data.get("mutational_status", {})

    # Filter only filled mutation fields
    present_mutations = {}
    for gene, info in mutation_block.items():
        if any(info.values()):  # Keep only if at least one value is non-empty
            present_mutations[gene] = info

    if present_mutations:
        all_mutation_data.append({
            "document_title": doc_title,
            "mutational_status": present_mutations
        })

# Save final output
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_mutation_data, f, indent=4)

print(f"✅ Extracted non-empty mutation fields to: {output_file}")
