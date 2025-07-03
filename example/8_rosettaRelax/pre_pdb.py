import os
import shutil

# Define directory paths
input_dir = '../../../ProteinMPNN-main/inputs/test'  # Path to the merged PDB files
pdb_dir = './pep_protein'  # Target directory (merged files will be copied here)
output_dir = 'input'  # Output directory (processed results will be stored here)

# Delete and recreate the output_dir to ensure no interference from previous results
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)  # Delete the directory
os.makedirs(output_dir)  # Create an empty directory

# Copy merged PDB files from input_dir to pdb_dir
if os.path.exists(pdb_dir):
    shutil.rmtree(pdb_dir)  # Delete target directory (if exists)
os.makedirs(pdb_dir)  # Create the target directory

# Iterate through the files and copy them
for file_name in os.listdir(input_dir):
    if file_name.endswith('.pdb'):  # Only copy PDB files
        source_path = os.path.join(input_dir, file_name)
        destination_path = os.path.join(pdb_dir, file_name)
        shutil.copy2(source_path, destination_path)  # Copy file while preserving metadata

# Amino acid one-letter to three-letter code mapping
aa_map = {
    'A': 'ALA', 'C': 'CYS', 'D': 'ASP', 'E': 'GLU', 'F': 'PHE', 'G': 'GLY',
    'H': 'HIS', 'I': 'ILE', 'K': 'LYS', 'L': 'LEU', 'M': 'MET', 'N': 'ASN',
    'P': 'PRO', 'Q': 'GLN', 'R': 'ARG', 'S': 'SER', 'T': 'THR', 'V': 'VAL',
    'W': 'TRP', 'Y': 'TYR', 'X': 'UNK', 'B': 'ASX', 'Z': 'GLX'
}

def parse_fa_file(fa_path):
    """Parse the FASTA file and return the sequences and sample numbers"""
    sequences = []
    sample_numbers = []
    with open(fa_path, 'r') as fa_file:
        lines = fa_file.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('>T='):
            # Extract sample number from the header line
            tokens = line.split(',')
            sample_number = None
            for token in tokens:
                token = token.strip()
                if token.startswith('sample='):
                    sample_number = token[len('sample='):]
                    break
            if sample_number is None:
                sample_number = 'unknown'
            sample_numbers.append(sample_number)
            # The next line contains the sequence
            i += 1
            if i < len(lines):
                seq_line = lines[i].strip()
                sequences.append(seq_line)
            else:
                print(f"Sequence missing after header in {fa_path}")
                sequences.append('')
        else:
            i += 1
    return sequences, sample_numbers

def modify_pdb_lines(pdb_lines, sequence):
    """Modify the residue names in the PDB lines for chain 0 according to the sequence"""
    modified_pdb_lines = []
    seq_residue_index = 0
    prev_res_seq_num = None
    for line in pdb_lines:
        if line.startswith('ATOM'):
            # Extract the chain identifier (column 22)
            chain_id = line[21].strip()
            if chain_id == '0':
                # Extract residue sequence number (columns 23-26)
                res_seq_num = line[22:26].strip()
                # Check if residue sequence number has changed
                if res_seq_num != prev_res_seq_num:
                    # Move to the next residue in the sequence
                    if seq_residue_index < len(sequence):
                        one_letter_aa = sequence[seq_residue_index]
                        three_letter_aa = aa_map.get(one_letter_aa, 'UNK')
                        three_letter_aa = three_letter_aa.ljust(3)[:3]
                        seq_residue_index += 1
                    else:
                        print("Sequence shorter than number of residues in PDB for chain 0")
                        three_letter_aa = 'UNK'
                    prev_res_seq_num = res_seq_num
                # Replace residue name in columns 18-20 (positions 17-20)
                line = line[:17] + three_letter_aa + line[20:]
            # Add the modified line
            modified_pdb_lines.append(line)
        else:
            # Non-ATOM lines are copied without modification
            modified_pdb_lines.append(line)
    return modified_pdb_lines

# Read FASTA files directory
fa_dir = '../../../ProteinMPNN-main/outputs/example_2_outputs/seqs'

# Process each PDB file in the pdb_dir
for pdb_filename in os.listdir(pdb_dir):
    if pdb_filename.endswith('.pdb'):
        # Get the full path to the PDB file
        pdb_path = os.path.join(pdb_dir, pdb_filename)
        
        # Extract the ID from the filename
        base_name = os.path.splitext(pdb_filename)[0]
        parts = base_name.split('_')
        ID = parts[-1]
        
        # Construct the corresponding FASTA file path
        fa_filename = base_name + '.fa'
        fa_path = os.path.join(fa_dir, fa_filename)
        
        # Check if the FASTA file exists
        if not os.path.exists(fa_path):
            print(f"FA file {fa_filename} not found for PDB file {pdb_filename}")
            continue
        
        # Parse the FASTA file to get sequences and sample numbers
        sequences, sample_numbers = parse_fa_file(fa_path)
        
        # Read the PDB file lines
        with open(pdb_path, 'r') as pdb_file:
            pdb_lines = pdb_file.readlines()
        
        # For each sequence, modify the PDB lines accordingly
        for seq_index, sequence in enumerate(sequences):
            modified_pdb_lines = modify_pdb_lines(pdb_lines, sequence)
            sample_number = sample_numbers[seq_index]
            output_filename = f"{base_name}_sample{sample_number}.pdb"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'w') as out_file:
                out_file.writelines(modified_pdb_lines)
        print(f"Processed PDB file {pdb_filename}")
