#!/bin/bash
#SBATCH -J caver_analysis
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err
#SBATCH -t 1-00:00:00
#SBATCH --mem=20G
#SBATCH -p v6_384

# ========== Ŀ¼Ԥ���� ==========
# �����ؽ����Ŀ¼
SCRIPT_DIR="."
INPUT_ROOT="${SCRIPT_DIR}/.."
PDB_SOURCE="${INPUT_ROOT}/pro_pdb"
PDB_ROOT="${INPUT_ROOT}/inputs/pdb_folders"
OUTPUT_ROOT="${INPUT_ROOT}/output"
PRO_PDB_DIR="${INPUT_ROOT}/pro_pdb"

rm -rf "${OUTPUT_ROOT}"
mkdir -p "${OUTPUT_ROOT}"
rm -rf "${PRO_PDB_DIR}"
mkdir -p "${PRO_PDB_DIR}"




# ��scored_pdbs�е����ݸ��Ƶ�pro_pdb
SCRORED_PDBS_DIR="../../10_InterfaceAnalyzer/scored_pdbs"
if [ -d "${SCRORED_PDBS_DIR}" ]; then
    cp "${SCRORED_PDBS_DIR}"/*.pdb "${PRO_PDB_DIR}/"
    echo "Copied PDB files from ${SCRORED_PDBS_DIR} to ${PRO_PDB_DIR}"
else
    echo "Warning: ${SCRORED_PDBS_DIR} does not exist"
fi


# ����pdb_foldersĿ¼�ṹ
mkdir -p "${PDB_ROOT}"
find "${PDB_SOURCE}" -maxdepth 1 -type f -name "*.pdb" | while read PDB_FILE; do
    PDB_NAME=$(basename "${PDB_FILE}" .pdb)
    TARGET_DIR="${PDB_ROOT}/${PDB_NAME}"
    mkdir -p "${TARGET_DIR}"
    cp "${PDB_FILE}" "${TARGET_DIR}/"
done

# ========== ����������� ==========
CAVER_HOME="../../../../caver_3.0.2/caver_3.0/caver"
CONFIG_FILE="${SCRIPT_DIR}/config.txt"
mapfile -t PDB_DIRS < <(find "${PDB_ROOT}" -mindepth 1 -maxdepth 1 -type d)

# ��� PDB_DIRS �Ƿ�Ϊ��
echo "PDB_DIRS length: ${#PDB_DIRS[@]}"
echo "PDB_DIRS: ${PDB_DIRS[*]}"

TOTAL_PDB=${#PDB_DIRS[@]}
MAX_TASKS=$((TOTAL_PDB < 20 ? TOTAL_PDB : 20))
PER_TASK=$(( (TOTAL_PDB + MAX_TASKS - 1) / MAX_TASKS ))

# ========== �����ύ ==========
for ((i=0; i<MAX_TASKS; i++)); do
    START=$((i * PER_TASK))
    END=$(( (i+1) * PER_TASK - 1 ))
    [ $END -ge $TOTAL_PDB ] && END=$((TOTAL_PDB-1))
    [ $START -ge $TOTAL_PDB ] && break

    # Ϊÿ������������Ҫ�����PDB·���б�
    TASK_PATHS=()
    for (( idx=START; idx<=END; idx++ )); do
        TASK_PATHS+=("${PDB_DIRS[idx]}")
    done

    # ��·���б�ת��Ϊ�ַ�������
    TASK_PATHS_STR=$(printf "%s\n" "${TASK_PATHS[@]}")

    sbatch <<EOT
#!/bin/bash
#SBATCH -J caver_${i}
#SBATCH -o ${OUTPUT_ROOT}/task_${i}.%j.out
#SBATCH -e ${OUTPUT_ROOT}/task_${i}.%j.err
#SBATCH -t 1-00:00:00
#SBATCH --mem=20G
#SBATCH -p v6_384

# �������������½���·���б�
while IFS= read -r PDB_DIR; do
    [ -z "\${PDB_DIR}" ] && continue  # ��������
    PDB_NAME=\$(basename "\${PDB_DIR}")
    OUTPUT_DIR="${OUTPUT_ROOT}/\${PDB_NAME}"

    # ������Ϣ
    echo "����PDBĿ¼: \${PDB_DIR}"
    mkdir -vp "\${OUTPUT_DIR}"

    # ����Caver
    java -Xmx15000m -cp ${CAVER_HOME}/lib \\
         -jar ${CAVER_HOME}/caver.jar \\
         -home ${CAVER_HOME} \\
         -pdb "\${PDB_DIR}" \\
         -conf "${CONFIG_FILE}" \\
         -out "\${OUTPUT_DIR}"
done <<EOF
${TASK_PATHS_STR}
EOF
EOT
done

echo "���ύ $(( (END >= 0 && i > 0) ? i : 0 )) �������� ${TOTAL_PDB} ��PDB�ṹ"
