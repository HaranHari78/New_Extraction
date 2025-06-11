import os
import json
import re
from pathlib import Path

# 🔹 Input folder (field-level JSON files)
field_input_dir = Path(r"C:\Users\HariharaM12\PycharmProjects\New_project\output\fields")

# 🔹 Output path for merged mutational_status results
mutation_output_path = Path(r"C:\Users\HariharaM12\PycharmProjects\New_project\output\merged_mutational_status.json")

# 🔹 Create output directory if needed
os.makedirs(mutation_output_path.parent, exist_ok=True)

# 🔹 Helper: sanitize filenames
def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# 🔹 Collect all cleaned mutational_status results
merged_data = []

# 🔁 Read and filter each JSON file
for filename in os.listdir(field_input_dir):
    if not filename.endswith(".json"):
        continue

    input_path = field_input_dir / filename
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content:
            print(f"⚠️ Skipping empty file: {filename}")
            continue

        data = json.loads(content)
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        continue

    document_title = data.get("document_title", filename.replace(".json", ""))
    mutational_status = data.get("mutational_status", {})

    # Extract only non-empty gene entries
    filtered_genes = {
        gene: values for gene, values in mutational_status.items()
        if any(values.get(k) for k in ("status", "date", "evidence"))
    }

    if filtered_genes:
        merged_data.append({
            "document_title": document_title,
            "mutational_status": filtered_genes
        })

# ✅ Save all cleaned mutation results to one file
with open(mutation_output_path, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=4)

print(f"✅ Merged mutation file saved to → {mutation_output_path}")
