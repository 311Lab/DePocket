# PepInhibitor
A structure-guided de novo peptide design pipeline integrating TERM-based backbone generation, ProteinMPNN sequence design, and multi-criteria screening with MD refinement for substrate-blocking inhibitor discovery. This inhibitory peptide design project is applicable to peptides that bind to the active pocket of the target protein and exert inhibitory effects by blocking substrate entry into the active center, such as inhibitory peptides for XO.

# Build Instructions
Install Mosaist, FreeSASA, Boost, Caver, and ProteinMPNN in the same directory as DePocket-main. Also, create a database/ folder to store single-chain protein databases. The directory structure should look like this:

project_root/

├── DePocket-main/

├── Mosaist/

├── freesasa-2.0.3/

├── boost_1_73_0/

├── caver_3.0.2/

├── ProteinMPNN-main/

└── database/


# Main Pipeline

The backbone generation code is  is derived from the https://github.com/swanss/peptide_design project.


## Input Setup:

1. Replace example/input_files/protein.pdb with your target protein PDB file. Keep the name as protein.pdb.

2. Replace partition names in all .sh files: change #SBATCH -p v6_384 to the actual partition on your HPC system.

3. Modify the targetSel residues in example/1_generateSeeds/run_generateSeeds.sh to amino acids within ~20 Å of the active pocket

4. Modify the active site center coordinates in both:5_backboneScreen/min_distance.py    11_caver/inputs/config.txt

5. In 10_InterfaceAnalyzer/run.sh, replace the -fixedchains parameter with the correct chain IDs of your target protein.


## Step-by-Step Instructions:

Run example/1_generateSeeds/run_generateSeeds.sh

Run 2_findOverlaps/run_findoverlaps_array.sh

Run 3_buildSeedGraph/run_buildSeedGraph.sh

Run 4_samplePaths/run_samplepaths.sh

Run 4_samplePaths/contact_scr.py

Run 5_backboneScreen/min_distance.py

Activate the conda environment mlfold corresponding to ProteinMPNN, as described at: https://github.com/dauparas/ProteinMPNN

Run 6_sequenceGenerate/run_MPNN.py

(Optional) Run 7_sequenceBasedML/extract_fasta.py, and the generated combined.fasta will contain sequences of candidate peptides. You can use sequence-based ML models to predict physicochemical properties and remove undesirable peptides.

Run 8_rosettaRelax/pre_pdb.py

Run 8_rosettaRelax/sbatch batch.sh

Run 10_InterfaceAnalyzer/run.sh (update the path to your Rosetta executable)

Run 10_InterfaceAnalyzer/update_sequences.py

Run 10_InterfaceAnalyzer/peptide_only.py

Run 11_caver/inputs/caver.sh

Run 11_caver/summary.py

Run 11_caver/sequence.py

Run 12_alphafold/gen_af3_json.py

Upload the generated JSON file to the AlphaFold3 web server (https://alphafoldserver.com/) under “Upload JSON” and save as a draft. Then submit each draft and extract the downloaded result packages to 12_alphafold/AF_pre/

Run 12_alphafold/calculate_rmsd.py

At this point, the files in 12_alphafold/result/ are candidate peptides (PDBs) and peptide–target protein complexes (PDBs) obtained after energy minimization and filtering by binding stability, blocking effect, and conformational consistency.

The peptide–target protein complexes need to undergo molecular dynamics (MD) simulations to obtain MD-stable conformations. Scripts and configuration files for batch MD simulations using GROMACS are provided in example/13_MD. The pdb folder stores the candidate peptide PDB files, and MD results are stored in the results folder.

In each MD result directory, run gmx_mpi rms -s md.tpr -f md.xtc -o rmsd.xvg -n index.ndx ，In the interactive interface, input 4 and 37 respectively to obtain the RMSD and calculate its standard deviation.

Run "gmx_mpi trjconv -f md.xtc -s md.tpr -n index.ndx -o frame.pdb -sep -dt 5000" to extract MD-stable complex structures. Compare blocking effects in PyMOL.

Calculate the RMSD between the monomeric structure predicted by AF3 and the MD-stable conformation. Those with RMSD < 1 Å are considered final designed inhibitory peptides. The threshold may be adjusted according to the design difficulty of different targets.


