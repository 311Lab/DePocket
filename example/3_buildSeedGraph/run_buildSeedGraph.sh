#!/bin/bash
#
#SBATCH -J buildSeedGraph 
#SBATCH -o buildSeedGraph.%A.out
#SBATCH -e buildSeedGraph.%A.err
#SBATCH -p v6_384
#SBATCH -t 1-00:00
#SBATCH -n 1 
#SBATCH --mem=60G

peptide_design=../..

seedBin=../1_generateSeeds/output/extendedfragments.bin
out="protein_seedGraph.adj"
overlaps=../2_findOverlaps/output/
optional_arg="--omitSeedsWithoutOverlaps" # omit this flag if you want to include seeds that do not overlap other seeds in the graph

SECONDS=0

srun $peptide_design/bin/buildSeedGraph --seedBin $seedBin --out $out --overlaps $overlaps $optional_arg

ELAPSED="Elapsed: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
echo $ELAPSED

exit 0

