#!/bin/bash
#
#SBATCH -J interface_analysis   
#SBATCH -o interface_analysis_batch.%A.out   
#SBATCH -e interface_analysis_batch.%A.err   
#SBATCH -p v6_384               
#SBATCH -t 7-00:00              
#SBATCH --mem=16G               


export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8


SCORE_JD2=../../../../soft/rosetta_src_2019.07.60616_bundle/main/source/bin/score_jd2.mpi.linuxgccrelease
INTERFACE_ANALYZER=../../../../soft/rosetta_src_2019.07.60616_bundle/main/source/bin/InterfaceAnalyzer.mpi.linuxgccrelease


PEPTIDE_DIR=../8_rosettaRelax/relaxed


SCORED_PDB_DIR=./scored_pdbs

OUTPUT_CSV=./interface_analysis_summary.csv


rm -rf $SCORED_PDB_DIR
mkdir -p $SCORED_PDB_DIR


echo "description,total_score,complex_normalized,dG_cross,dG_cross/dSASAx100,dG_separated,dSASA_int,dG_separated/dSASA_int,dSASA_hphobic,dSASA_polar,delta_unsatHbonds,hbond_E_fraction,hbonds_int,nres_all,nres_int,packstat,per_residue_energy_int,sc_value,side1_normalized,side1_score,side2_normalized,side2_score" > $OUTPUT_CSV


echo "-ignore_unrecognized_res true" > no_pack_input_options.txt


for PDB_FILE in $PEPTIDE_DIR/*.pdb; do
    FILENAME=$(basename "$PDB_FILE" .pdb)
    
  
    $SCORE_JD2 \
    -s $PDB_FILE \
    -no_optH false \
    -ignore_unrecognized_res \
    -out:pdb
    
   
    mv ${FILENAME}_0001.pdb $SCORED_PDB_DIR/${FILENAME}_scored.pdb
done


for PDB_FILE in $SCORED_PDB_DIR/*.pdb; do
    FILENAME=$(basename "$PDB_FILE" .pdb)
    
    
    INTERFACE_OUTPUT=$(mktemp)
    
    
    $INTERFACE_ANALYZER \
    -s $PDB_FILE \
    -fixedchains A B C J K L \
    @no_pack_input_options.txt \
    -out:file:scorefile $INTERFACE_OUTPUT
    
   
    RESULT=$(grep SCORE $INTERFACE_OUTPUT | grep -v SEQUENCE | awk -v desc="$FILENAME" '{
        dg_separated=$6;
        dsasa_int=$8;
        if (dsasa_int != 0) {
            ratio=(dg_separated/dsasa_int)*100;
        } else {
            ratio="NA";
        }
        print desc","$2","$3","$4","$5","dg_separated","dsasa_int","ratio","$9","$10","$11","$12","$13","$14","$15","$16","$17","$18","$19","$20","$21","$22","$23
    }')
    
    
    echo "$RESULT" >> $OUTPUT_CSV
    
    
    rm $INTERFACE_OUTPUT
done

echo "Interface analysis completed and summarized into $OUTPUT_CSV."
