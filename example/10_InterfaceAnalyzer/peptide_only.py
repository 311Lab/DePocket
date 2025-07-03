import os
import csv
import shutil

# Directories
peptide_only_dir = './peptide_only'  # Directory where the PDB files are stored
scored_pdbs_dir = './scored_pdbs'  # Directory where the scored PDB files are located
seqs_dir = '../../../ProteinMPNN-main/outputs/example_2_outputs/seqs'  # Directory where the .fa files are stored
output_csv = 'peptide_sequence.csv'

# Ensure the peptide_only directory exists (create if not)
if not os.path.exists(peptide_only_dir):
    os.makedirs(peptide_only_dir)
    print(f"Directory '{peptide_only_dir}' was created.")

# Function to copy and process PDB files: remove the protein part
def process_pdb(pdb_file, output_pdb_file):
    with open(pdb_file, 'r') as infile:
        lines = infile.readlines()
    
    # Find the first TER and stop before it (i.e., remove the protein part)
    with open(output_pdb_file, 'w') as outfile:
        for line in lines:
            if line.startswith("TER"):
                break
            outfile.write(line)

# Copy and process PDB files from scored_pdbs to peptide_only_dir
for filename in os.listdir(scored_pdbs_dir):
    if filename.endswith('.pdb'):
        pdb_file = os.path.join(scored_pdbs_dir, filename)
        output_pdb_file = os.path.join(peptide_only_dir, filename)
        process_pdb(pdb_file, output_pdb_file)
        print(f"Processed {filename} and saved to {output_pdb_file}")

# Prepare a list to hold peptide sequences and names
peptide_sequences = []

# Function to extract peptide sequence based on sample number from .fa file
def extract_sequence_from_fa(file_path, sample_num):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if f"sample={sample_num}" in lines[i]:
                # The next line contains the peptide sequence
                return lines[i + 1].strip()  # Remove any extra whitespace or newline
    return None  # If not found, return None

# Iterate over all PDB files in the peptide_only directory
for filename in os.listdir(peptide_only_dir):
    if filename.endswith('.pdb'):
        # Use the PDB file name as the peptide name
        peptide_name = filename.split('.')[0]  # Strip the extension to get the peptide name

        # Extract the sample number from the corresponding .fa file
        sample_num = None
        # Check if the file is in the correct format and extract sample number
        if 'sample' in peptide_name:
            sample_num = int(peptide_name.split('sample')[1].split('_')[0])  # Extract sample number after 'sample='

        if sample_num:
            # Get the corresponding .fa file name
            fa_filename = peptide_name.split('_sample')[0] + '.fa'  # Corresponding .fa file should have the same prefix
            file_path = os.path.join(seqs_dir, fa_filename)

            # If the .fa file exists, extract the peptide sequence
            if os.path.exists(file_path):
                sequence = extract_sequence_from_fa(file_path, sample_num)
                
                if sequence:
                    peptide_sequences.append([peptide_name, sequence])

# Write the peptide sequences to a CSV file
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Peptide Name', 'Peptide Sequence'])  # Write the header
    writer.writerows(peptide_sequences)  # Write the peptide sequences data

print(f"Total peptides extracted: {len(peptide_sequences)}")


# Delete the existing file in the target directory if it exists
if os.path.exists(target_csv):
    os.remove(target_csv)
    print(f"Deleted existing peptide_sequence.csv in {target_dir}")

# Copy the new peptide_sequence.csv to the target directory
shutil.copy(output_csv, target_csv)
print(f"Copied {output_csv} to {target_dir}")
