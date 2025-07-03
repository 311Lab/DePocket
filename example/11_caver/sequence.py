import os
import csv
import shutil
import math

# Set the related directories
summary_csv = 'summary_tunnel_characteristics.csv'  # Summary file with tunnel characteristics
peptide_sequence_csv = '../10_InterfaceAnalyzer/peptide_sequence.csv'  # Peptide sequence file from InterfaceAnalyzer
good_results_dir = './good_results'  # Directory to store selected PDB files
pro_pdb_dir = './pro_pdb'  # Directory where the PDB files are stored

# Ensure the good_results directory exists and clear it
if os.path.exists(good_results_dir):
    shutil.rmtree(good_results_dir)  # Remove the directory and its contents
os.makedirs(good_results_dir)  # Recreate the directory

# Read the summary_tunnel_characteristics.csv file
pdb_info = []
with open(summary_csv, mode='r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip the header
    for row in reader:
        pdb_name = row[0]
        length_str = row[8]  # Length is at index 8 (zero-based index)
        
        # Try converting Length to a numeric value (float)
        try:
            if length_str.strip() != '-' and length_str != '':  # Skip if length is missing or '-'
                length = float(length_str)  # Convert to float
                pdb_info.append((pdb_name, length))  # Store pdb_name and length
            else:
                pdb_info.append((pdb_name, float('nan')))  # If length is missing, store NaN
        except ValueError:
            print(f"Warning: Unable to convert Length value for {pdb_name}: {length_str}")
            pdb_info.append((pdb_name, float('nan')))  # If conversion fails, store NaN

# Sort the peptides based on their length in descending order
pdb_info.sort(key=lambda x: x[1], reverse=True)  # Sort by length, largest to smallest

# Calculate the number of peptides to keep (top 30%)
top_30_percent_count = math.ceil(len(pdb_info) * 0.3)

# Select the top 30% peptides
top_30_pdb_info = pdb_info[:top_30_percent_count]

# Copy the PDB files of the selected peptides to the good_results directory
for pdb_name, length in top_30_pdb_info:
    pdb_file = os.path.join(pro_pdb_dir, f"{pdb_name}.pdb")
    if os.path.exists(pdb_file):
        shutil.copy(pdb_file, good_results_dir)  # Copy the PDB file to the good_results directory
    else:
        print(f"Warning: PDB file {pdb_name}.pdb does not exist.")  # If the PDB file doesn't exist, print a warning

# Read the peptide_sequence.csv file and filter the selected peptides
peptide_data = []
with open(peptide_sequence_csv, mode='r') as seq_file:
    reader = csv.reader(seq_file)
    header = next(reader)  # Read the header
    peptide_data.append(header + ['caver_length'])  # Add 'caver_length' column
    
    for row in reader:
        pdb_name_without_ext = row[0]  # Name without '.pdb'
        sequence = row[1]
        
        # Find the corresponding Length and keep only the top 30% peptides
        for pdb_name, length in top_30_pdb_info:
            if pdb_name == pdb_name_without_ext:
                peptide_data.append(row + [length])  # Add 'caver_length' column to the row
                break

# Write the filtered data to a new peptide_sequence.csv file
new_peptide_sequence_csv = './peptide_sequence.csv'
with open(new_peptide_sequence_csv, mode='w', newline='') as new_seq_file:
    writer = csv.writer(new_seq_file)
    writer.writerows(peptide_data)  # Write the filtered data

print(f"Operation completed. Top 30% peptides have been copied to {good_results_dir}, and the new peptide_sequence.csv has been saved as {new_peptide_sequence_csv}.")
