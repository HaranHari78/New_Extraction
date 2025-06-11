import os
import json
import re
from collections import defaultdict

# Input directory with full structured JSONs per patient
input_dir = r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields"
# Output directory where field-wise JSONs will be saved
output_dir = os.path.join(input_dir, "..", "merged_fields")
os.makedirs(output_dir, exist_ok=True)

# Utility to check if a field contains useful data
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
        doc = json.load(f)

    doc_title = doc.get("document_title", filename.replace(".json", ""))

    for field, value in doc.items():
        if field == "document_title":
            continue
        if has_data(value):
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
