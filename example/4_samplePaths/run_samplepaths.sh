#!/bin/bash
#
#SBATCH -J samplePaths
#SBATCH -o samplePaths.%A.out
#SBATCH -e samplePaths.%A.err
#SBATCH -p v6_384
#SBATCH -t 2-00:00:00
#SBATCH -n 1
#SBATCH --mem=30G

peptide_design=../..

targetPDB=../input_files/protein.pdb
seedBin=../1_generateSeeds/output/extendedfragments.bin
seedGraph=../3_buildSeedGraph/protein_seedGraph.adj
numPaths=4000
config=../input_files/singlechainDB.configfile
base=1LB6

SECONDS=0

srun $peptide_design/bin/samplePaths --targetPDB $targetPDB --seedBin $seedBin --seedGraph $seedGraph --numPaths $numPaths --config $config --base $base --writeTopology --countContacts 

ELAPSED="Elapsed: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
echo $ELAPSED

exit 0

