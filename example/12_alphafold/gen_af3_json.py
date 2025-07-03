import json
import pandas as pd
import os

# Define the input CSV file path
csv_path = "../11_caver/peptide_sequence.csv"

# Set the maximum number of peptide sequences per JSON file
max_entries_per_file = 20

# Define the output directory for JSON files
output_dir = "./"
os.makedirs(output_dir, exist_ok=True)

# Read the CSV file
df = pd.read_csv(csv_path)

# Extract required columns: "Peptide Name" and "Peptide Sequence"
peptides = df[['Peptide Name', 'Peptide Sequence']].to_dict(orient='records')

# Calculate the total number of JSON files needed
total_json_files = (len(peptides) + max_entries_per_file - 1) // max_entries_per_file

# Generate JSON files in batches of 20 sequences each
for i, start in enumerate(range(0, len(peptides), max_entries_per_file), start=1):
    batch = peptides[start:start + max_entries_per_file]

    # Construct the JSON structure as a list (required by AlphaFold Server)
    json_data = [
        {
            "name": item['Peptide Name'],  # Job name from the first column of CSV
            "modelSeeds": [],  # Leave empty for automatic random seed assignment
            "sequences": [
                {
                    "proteinChain": {
                        "sequence": item['Peptide Sequence'],  # Peptide sequence
                        "count": 1  # Default to one copy of the peptide
                    }
                }
            ],
            "dialect": "alphafoldserver",
            "version": 1
        }
        for item in batch
    ]

    # Save the JSON file
    json_filename = os.path.join(output_dir, f"{i}.json")
    with open(json_filename, "w") as json_file:
        json.dump(json_data, json_file, indent=4)
# Define the directory path
dir_path = "./AF_pre"

# Create the directory if it does not exist
os.makedirs(dir_path, exist_ok=True)

print(f"? Successfully generated {total_json_files} JSON files, each containing up to {max_entries_per_file} peptide sequences.")
