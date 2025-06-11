import os
import json
import re
from collections import defaultdict

# Input directory with structured JSONs per patient
input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields"
# Output directory where merged field-wise JSONs will be saved
output_dir = os.path.join(input_dir, "..", "merged_fields")
os.makedirs(output_dir, exist_ok=True)

# Utility to check if a field or subfield has useful data
def has_data(value):
    if isinstance(value, dict):
        return any(has_data(v) for v in value.values())
    elif isinstance(value, list):
        return any(has_data(item) for item in value)
    return bool(value and str(value).strip())

# Accumulator for each field
field_data = defaultdict(list)

# Process each document JSON file
for filename in os.listdir(input_dir):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(input_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
            print(f"⚠️ Skipping empty file: {filename}")
            continue
        try:
            doc = json.loads(content)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in file: {filename}")
            continue

    doc_title = doc.get("document_title", filename.replace(".json", ""))

    for field, value in doc.items():
        if field == "document_title":
            continue

        # Special handling for mutational_status: always include the document
        if field == "mutational_status":
            if isinstance(value, dict):
                cleaned = {gene: info for gene, info in value.items() if has_data(info)}
            else:
                cleaned = {}
            field_data["mutational_status"].append({
                "document_title": doc_title,
                "mutational_status": cleaned
            })

        # Standard handling for other fields (only include if non-empty)
        elif isinstance(value, dict):
            cleaned = {k: v for k, v in value.items() if has_data(v)}
            if cleaned:
                field_data[field].append({
                    "document_title": doc_title,
                    field: cleaned
                })

        elif isinstance(value, list):
            cleaned_list = [v for v in value if has_data(v)]
            if cleaned_list:
                field_data[field].append({
                    "document_title": doc_title,
                    field: cleaned_list
                })

        elif has_data(value):
            field_data[field].append({
                "document_title": doc_title,
                field: value
            })

# Save one file per field
for field_name, records in field_data.items():
    out_path = os.path.join(output_dir, f"{field_name}.json")
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(records, out_f, indent=4)
    print(f"✅ Saved: {field_name}.json with {len(records)} entries")
