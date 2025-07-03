import os
import shutil
import pandas as pd

# File paths
csv_file = '1LB6_fused_paths.csv'  # CSV file path
path_structures_folder = 'path_structures'  # Folder where PDB files are stored
output_folder = 'output'  # Folder to store the copied PDB files
output_all_folder = 'output_all'  # New folder to store the combined PDB files
protein_pdb = '../input_files/protein.pdb'  # Path to the protein PDB file
test_folder = '../../../ProteinMPNN-main/inputs/test'  # Path to the test folder for ProteinMPNN

# Check and create the output folders. If the folders exist, delete them and create new ones.
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)  # Delete the existing output folder
os.makedirs(output_folder)  # Create a new output folder

if os.path.exists(output_all_folder):
    shutil.rmtree(output_all_folder)  # Delete the existing output_all folder
os.makedirs(output_all_folder)  # Create a new output_all folder

# Check and create the test folder for ProteinMPNN. If it exists, delete and recreate it.
if os.path.exists(test_folder):
    shutil.rmtree(test_folder)  # Delete the existing test folder
os.makedirs(test_folder)  # Create a new test folder

# Read the CSV file
df = pd.read_csv(csv_file)

# Calculate num_interface_contacts / path_len
df['contact_ratio'] = df['num_interface_contacts'] / df['path_len']

# Filter rows where contact_ratio >= 4
filtered_df = df[df['contact_ratio'] >= 4]

# Extract the 'name' column of the rows that meet the condition
names_to_search = filtered_df['name']

# Loop through these names, search for the corresponding PDB files, and copy them to the output folder
for name in names_to_search:
    pdb_filename = name + ".pdb"  # Concatenate the PDB file name
    pdb_filepath = os.path.join(path_structures_folder, pdb_filename)  # Create the full path for the PDB file
    
    # Check if the PDB file exists in path_structures folder
    if os.path.exists(pdb_filepath):
        # Copy the PDB file to the output folder
        shutil.copy(pdb_filepath, os.path.join(output_folder, pdb_filename))
        print("File copied: " + pdb_filename)

        # Now create the combined PDB file in output_all folder
        combined_pdb_filename = pdb_filename
        combined_pdb_filepath = os.path.join(output_all_folder, combined_pdb_filename)

        # Read the protein PDB
        with open(protein_pdb, 'r') as protein_file:
            protein_lines = protein_file.readlines()

        # Read the peptide PDB (copied in the output folder)
        with open(os.path.join(output_folder, pdb_filename), 'r') as peptide_file:
            peptide_lines = peptide_file.readlines()

        # Combine the peptide and protein PDB files (peptide first, then protein)
        with open(combined_pdb_filepath, 'w') as combined_file:
            # Write peptide atoms first
            combined_file.writelines(peptide_lines)
            # Write protein atoms after peptide
            combined_file.writelines(protein_lines)

        print(f"Combined PDB created: {combined_pdb_filename}")

        # Copy the combined PDB file to the test folder for ProteinMPNN
        shutil.copy(combined_pdb_filepath, os.path.join(test_folder, combined_pdb_filename))
        print(f"File copied to ProteinMPNN test folder: {combined_pdb_filename}")
    else:
        print("File not found: " + pdb_filename)

print("Task complete. All PDB files matching the criteria have been copied, combined, and moved to ProteinMPNN test folder.")
