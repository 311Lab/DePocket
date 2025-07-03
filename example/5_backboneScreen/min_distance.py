# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from Bio import PDB

# Function to calculate Euclidean distance between two points
def calculate_distance(coord1, coord2):
    return np.linalg.norm(np.array(coord1) - np.array(coord2))

# Function to extract all atom coordinates from a PDB file
def get_atom_coordinates(pdb_file):
    parser = PDB.PDBParser(QUIET=True)  # Use PDBParser to parse the PDB file
    structure = parser.get_structure("structure", pdb_file)
    coords = []
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    coords.append(atom.coord)
    return coords

# Set target coordinates
target_coord = [37, 13.4, 18.1]

# Define file paths
output_folder = "../4_samplePaths/output"
test_folder = "../../../ProteinMPNN-main/inputs/test"
csv_file = "peptide_distances.csv"

# List to store peptide names and their corresponding shortest distances
data = []

# Iterate over all PDB files in the output folder
for pdb_file in os.listdir(output_folder):
    if pdb_file.endswith(".pdb"):
        pdb_path = os.path.join(output_folder, pdb_file)
        
        # Get all atom coordinates from the PDB file
        atom_coords = get_atom_coordinates(pdb_path)
        
        # Calculate the shortest distance from any atom to the target coordinates
        min_distance = min([calculate_distance(coord, target_coord) for coord in atom_coords])
        
        # Store the result in the data list
        data.append([pdb_file, min_distance])
        
        # If the distance is greater than 10 ?, delete the corresponding PDB file in the test folder
        if min_distance > 10:
            test_pdb_path = os.path.join(test_folder, pdb_file)
            if os.path.exists(test_pdb_path):
                os.remove(test_pdb_path)
                print(f"Deleted: {test_pdb_path}")

# Save the results to a CSV file
df = pd.DataFrame(data, columns=["PDB File", "Min Distance"])
df.to_csv(csv_file, index=False)

print(f"Results saved to {csv_file}")
