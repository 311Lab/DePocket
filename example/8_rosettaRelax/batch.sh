#!/bin/bash
#
#SBATCH -J batch_relax 
#SBATCH -o relax_batch.%j.out
#SBATCH -e relax_batch.%j.err
#SBATCH -p v6_384
#SBATCH -t 7-00:00
#SBATCH --ntasks-per-node=1
#SBATCH --mem=8G

# -*- coding: utf-8 -*- 
# --------------------- 可配置参数 ---------------------
MAX_JOBS=50               # 最大并行任务数
POLL_INTERVAL=30          # 队列检查间隔（秒）
OUTPUT_DIR="./relaxed"     # 输出目录
INPUT_DIR="./input"        # 输入目录
FA_DIR="../../../ProteinMPNN-main/outputs/example_2_outputs/seqs"  # FA文件目录
NSTRUCT=1                  # 每个结构运行次数
# -----------------------------------------------------

module load mpi/intel/17.0.5-cjj

# 初始化环境
rosetta_bin_dir="/public1/home/t0s000352/soft/rosetta_src_2019.07.60616_bundle/main/source/bin"
mkdir -p $OUTPUT_DIR
rm -rf $OUTPUT_DIR/*

# 获取当前batch_re作业的ID
batch_re_id=$SLURM_JOB_ID

# 预生成所有任务列表
declare -a task_queue
while IFS= read -r -d $'\0' pdb_file; do
    task_queue+=("$pdb_file")
done < <(find $INPUT_DIR -maxdepth 1 -name "*.pdb" -print0)
total_tasks=${#task_queue[@]}
task_index=0

# 作业提交主循环
while [ $task_index -lt $total_tasks ]; do
    # 获取当前运行中的作业数（排除自己）
    current_jobs=$(squeue -u $USER -h -o "%i" --states=PENDING,RUNNING | grep -v $batch_re_id | wc -l)
    
    # 计算可用槽位
    available_slots=$(( MAX_JOBS - current_jobs ))
    
    # 提交任务直到填满槽位或处理完所有任务
    while [ $available_slots -gt 0 ] && [ $task_index -lt $total_tasks ]; do
        pdb_file=${task_queue[$task_index]}
        ((task_index++))
        
        # ================ 作业生成逻辑 ================
        pdb_filename=$(basename "$pdb_file")
        base_name=${pdb_filename%.pdb}
        id_sample=${base_name#*fused-path_}
        ID=${id_sample%_sample*}
        sampleN=${id_sample#*_sample}

        # 获取FA文件信息
        fa_file="$FA_DIR/1LB6_fused-path_${ID}.fa"
        if [[ ! -f "$fa_file" ]]; then
            echo "[ERROR] FA file $fa_file not found for $pdb_filename" >> relax_batch.%j.out
            continue
        fi

        # 计算肽段长度
        peptide_length=$(sed -n '2p' "$fa_file" | tr -cd 'X' | wc -c)
        
        # 生成movemap文件
        movemap_file="$OUTPUT_DIR/movemap_${base_name}.txt"
        cat > $movemap_file <<EOF
RESIDUE * NO
RESIDUE 1 $peptide_length BBCHI
EOF

        # 生成作业脚本
        job_script="$OUTPUT_DIR/relax_${base_name}.sh"
        cat > $job_script <<JOBSCRIPT
#!/bin/bash
#SBATCH -J relax_${base_name}
#SBATCH -p v6_384
#SBATCH -t 7-00:00
#SBATCH --mem=8G
#SBATCH -o $OUTPUT_DIR/${base_name}.out
#SBATCH -e $OUTPUT_DIR/${base_name}.err

module load mpi/intel/17.0.5-cjj

$rosetta_bin_dir/relax.mpi.linuxgccrelease \\
  -in:file:s $pdb_file \\
  -nstruct $NSTRUCT \\
  -relax:default_repeats 1 \\
  -in:file:movemap $movemap_file \\
  -out:path:all $OUTPUT_DIR \\
  -out:file:scorefile $OUTPUT_DIR/score_${base_name}.sc \\
  -out:level 400

echo "relax_${base_name} completed" >> $OUTPUT_DIR/${base_name}.out
JOBSCRIPT

        # 提交作业
        sbatch $job_script
        echo "Submitted: $base_name (Job count: $((task_index))" >> relax_batch.%j.out
        
        ((available_slots--))
    done
    
    # 等待下一轮检查
    sleep $POLL_INTERVAL
done

# 等待所有作业完成
while [ $(squeue -u $USER -h -o "%i" --states=PENDING,RUNNING | grep -v $batch_re_id | wc -l) -gt 0 ]; do
    echo "Remaining jobs: $(squeue -u $USER -h -o "%i" --states=PENDING,RUNNING | grep -v $batch_re_id | wc -l)" >> relax_batch.%j.out
    sleep $POLL_INTERVAL
done

# 清理临时文件
rm -f $OUTPUT_DIR/movemap_*.txt
rm -f $OUTPUT_DIR/relax_*.sh

# 保留relaxed文件夹中的pdb文件，删除其他文件
find $OUTPUT_DIR -type f ! -name "*.pdb" -exec rm -f {} \;

# 记录运行时间
ELAPSED="Elapsed: $(($SECONDS / 3600))hrs $(($SECONDS / 60 % 60))min $(($SECONDS % 60))sec"
echo $ELAPSED >> relax_batch.%j.out

exit 0