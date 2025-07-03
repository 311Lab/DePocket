#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
from Bio import PDB

def extract_peptide_id(filename):
    """
    Extract ID of the form N_sampleM by searching for a pattern like:
    ..._<number>_sample<another_number>...
    Example: '1lb6_fused_path_11_sample3_0001_scored' => '11_sample3'
    Return None if not matched.
    """
    pattern = re.compile(r'[_-](\d+)_sample(\d+)', re.IGNORECASE)
    match = pattern.search(filename)
    if not match:
        return None
    return f"{match.group(1)}_sample{match.group(2)}"

def find_pdb_by_partial_id(pep_id, search_dir):
    """
    Look for a PDB file in search_dir where the filename CONTAINS pep_id (case-insensitive).
    Example: if pep_id='11_sample3', we look for '*11_sample3*.pdb' in the directory.
    """
    if not pep_id:
        return None
    for f in os.listdir(search_dir):
        if f.lower().endswith('.pdb') and pep_id.lower() in f.lower():
            return os.path.join(search_dir, f)
    return None

def load_structure(file_path, structure_id):
    """
    Load PDB or CIF using Biopython parser.
    """
    ext = os.path.splitext(file_path)[1].lower()
    parser = PDB.PDBParser(QUIET=True) if ext == '.pdb' else PDB.MMCIFParser(QUIET=True) if ext == '.cif' else None
    return parser.get_structure(structure_id, file_path) if parser else None

def calc_ca_rmsd(struct1, struct2):
    """
    Calculate standard RMSD for C-alpha atoms (in ?), already normalized by residue count.
    """
    residues1 = [res for res in struct1.get_residues() if PDB.is_aa(res, standard=True)]
    residues2 = [res for res in struct2.get_residues() if PDB.is_aa(res, standard=True)]
    
    if len(residues1) != len(residues2) or len(residues1) == 0:
        return None

    cas1, cas2 = [], []
    for r1, r2 in zip(residues1, residues2):
        if 'CA' not in r1 or 'CA' not in r2:
            return None
        cas1.append(r1['CA'])
        cas2.append(r2['CA'])

    super_imposer = PDB.Superimposer()
    super_imposer.set_atoms(cas1, cas2)
    super_imposer.apply(struct2.get_atoms())

    return super_imposer.rms

def main():
    af_pre_dir = './AF_pre'
    pep_only_dir = '../11_caver/good_results/pep_only'
    whole_dir = '../11_caver/good_results'
    out_csv = './RMSD.csv'
    result_dir = './result'
    pro_pep_dir = os.path.join(result_dir, 'pro_pep')

    # Overwrite the CSV
    with open(out_csv, 'w') as f:
        f.write("peptide_id,average_RMSD\n")

    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(pro_pep_dir, exist_ok=True)

    for subfolder in os.listdir(af_pre_dir):
        full_sub = os.path.join(af_pre_dir, subfolder)
        if not os.path.isdir(full_sub):
            continue

        # Find fold_..._model_0.cif
        cif_path = None
        for filename in os.listdir(full_sub):
            lower_file = filename.lower()
            if lower_file.endswith('_model_0.cif') and lower_file.startswith('fold_'):
                cif_path = os.path.join(full_sub, filename)
                break

        if not cif_path:
            continue

        # Extract the simplified peptide ID: N_sampleM
        pep_id = extract_peptide_id(os.path.basename(cif_path))
        if not pep_id:
            continue  # Skip if no valid pattern found

        # Find the corresponding designed PDB that CONTAINS pep_id
        designed_pdb = find_pdb_by_partial_id(pep_id, pep_only_dir)
        if not designed_pdb:
            continue

        # Load structures
        struct_pred = load_structure(cif_path, 'pred')
        struct_des = load_structure(designed_pdb, 'des')
        if not struct_pred or not struct_des:
            continue

        # Calculate average RMSD (C-alpha)
        avg_rmsd = calc_ca_rmsd(struct_des, struct_pred)
        if avg_rmsd is None:
            continue

        # Write to CSV
        with open(out_csv, 'a') as f:
            f.write(f"{pep_id},{avg_rmsd:.4f}\n")

        # If RMSD < 0.2, copy files
        if avg_rmsd < 0.2:
            dst_pep = os.path.join(result_dir, os.path.basename(designed_pdb))
            shutil.copyfile(designed_pdb, dst_pep)
            # Copy the peptide+protein complex
            whole_pdb = find_pdb_by_partial_id(pep_id, whole_dir)
            if whole_pdb:
                dst_whole = os.path.join(pro_pep_dir, os.path.basename(whole_pdb))
                shutil.copyfile(whole_pdb, dst_whole)

if __name__ == '__main__':
    main()
