#!/bin/bash
#
#SBATCH -J interface_analysis   # 作业名
#SBATCH -o interface_analysis_batch.%A.out   # 标准输出文件
#SBATCH -e interface_analysis_batch.%A.err   # 标准错误输出文件
#SBATCH -p v6_384               # 队列分区
#SBATCH -t 7-00:00              # 最大运行时间
#SBATCH --mem=16G               # 内存

# 对 ../8_rosettaRelax/relaxed 中的 pdb 评分并汇总到一个 .csv 文件中
# 设置 UTF-8 编码
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# 设置 Rosetta 可执行文件路径
SCORE_JD2=../../../../soft/rosetta_src_2019.07.60616_bundle/main/source/bin/score_jd2.mpi.linuxgccrelease
INTERFACE_ANALYZER=../../../../soft/rosetta_src_2019.07.60616_bundle/main/source/bin/InterfaceAnalyzer.mpi.linuxgccrelease

# PDB 文件所在目录
PEPTIDE_DIR=../8_rosettaRelax/relaxed

# 评分后的 PDB 存储目录
SCORED_PDB_DIR=./scored_pdbs
# 输出 CSV 文件
OUTPUT_CSV=./interface_analysis_summary.csv

# 步骤 1：删除旧文件并重新创建文件夹和 CSV 文件
rm -rf $SCORED_PDB_DIR
mkdir -p $SCORED_PDB_DIR

# 初始化 CSV 文件，写入表头
echo "description,total_score,complex_normalized,dG_cross,dG_cross/dSASAx100,dG_separated,dSASA_int,dG_separated/dSASA_int,dSASA_hphobic,dSASA_polar,delta_unsatHbonds,hbond_E_fraction,hbonds_int,nres_all,nres_int,packstat,per_residue_energy_int,sc_value,side1_normalized,side1_score,side2_normalized,side2_score" > $OUTPUT_CSV

# 创建 no_pack_input_options.txt 文件
echo "-ignore_unrecognized_res true" > no_pack_input_options.txt
# 这里可以添加其他需要的选项

# 步骤 2：评分所有的 PDB 文件
for PDB_FILE in $PEPTIDE_DIR/*.pdb; do
    FILENAME=$(basename "$PDB_FILE" .pdb)
    
    # 运行 score_jd2 进行评分
    $SCORE_JD2 \
    -s $PDB_FILE \
    -no_optH false \
    -ignore_unrecognized_res \
    -out:pdb
    
    # 移动评分后的 PDB 文件
    mv ${FILENAME}_0001.pdb $SCORED_PDB_DIR/${FILENAME}_scored.pdb
done

# 步骤 3：运行 InterfaceAnalyzer 进行界面分析并汇总结果
for PDB_FILE in $SCORED_PDB_DIR/*.pdb; do
    FILENAME=$(basename "$PDB_FILE" .pdb)
    
    # 临时文件存储输出
    INTERFACE_OUTPUT=$(mktemp)
    
    # 运行 InterfaceAnalyzer
    $INTERFACE_ANALYZER \
    -s $PDB_FILE \
    -fixedchains A B C J K L \
    @no_pack_input_options.txt \
    -out:file:scorefile $INTERFACE_OUTPUT
    
    # 提取结果并计算比值
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
    
    # 将结果添加到 CSV 文件中
    echo "$RESULT" >> $OUTPUT_CSV
    
    # 删除临时文件
    rm $INTERFACE_OUTPUT
done

echo "Interface analysis completed and summarized into $OUTPUT_CSV."
