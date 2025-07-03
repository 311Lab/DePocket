#!/bin/bash
#
#
#SBATCH -J generateSeeds
#SBATCH -o generateSeeds.%J.out
#SBATCH -e generateSeeds.%J.err
#SBATCH -t 1-00:00:00
#SBATCH --mem=20G
#SBATCH -p v6_384

peptide_design=../..

targetPDB=../input_files/protein.pdb
paramsFile=genSeeds.params

SECONDS=0

srun $peptide_design/bin/generateSeeds --targetPDB $targetPDB --paramsFile $paramsFile --targetSel '(chain A and resid 181-187) or (chain A and resid 195-204) or (chain A and resid 274-283) or (chain A and resid 739-741) or (chain A and resid 299-311) or (chain A and resid 334-335) or (chain A and resid 341-349) or (chain A and resid 355-383)'

ELAPSED="Elapsed: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
echo $ELAPSED

exit 0
  