# -*- coding: utf-8 -*-
import os
import subprocess
import shutil
import multiprocessing
import argparse


PEPTIDE_START = 38929  
GROMACS_ENV_NAME = "gromacs2024.3"  # Conda env name
PDB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdb")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
MDP_FILES = ["ions.mdp", "md.mdp", "minim.mdp", "npt.mdp", "nvt.mdp"]
# ==============================

def prepare_work_dir(pdb_path):
    
    name = os.path.splitext(os.path.basename(pdb_path))[0]
    work_dir = os.path.join(RESULTS_DIR, name)
    os.makedirs(work_dir, exist_ok=True)

    pdb_name = os.path.basename(pdb_path)
    shutil.copy(pdb_path, os.path.join(work_dir, pdb_name))
    for f in MDP_FILES:
        shutil.copy(os.path.join(os.path.dirname(__file__), f), os.path.join(work_dir, f))
    return work_dir, pdb_name

def run_pipeline(pdb_path, gpu_id):
    work_dir, pdb_name = prepare_work_dir(pdb_path)
    os.chdir(work_dir)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    gro_file = pdb_name.replace(".pdb", ".gro")

    bash_script = f"""
conda activate {GROMACS_ENV_NAME}

gmx_mpi pdb2gmx -f {pdb_name} -o {gro_file} -p topol.top -ignh << EOF
6
1
EOF

gmx_mpi editconf -f {gro_file} -o box.gro -c -d 3.0 -bt triclinic
gmx_mpi solvate -cp box.gro -cs spc216.gro -o solvated.gro -p topol.top
gmx_mpi grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr
echo 13 | gmx_mpi genion -s ions.tpr -o solvated_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15
gmx_mpi grompp -f minim.mdp -c solvated_ions.gro -p topol.top -o em.tpr -maxwarn 3
gmx_mpi mdrun -v -deffnm em

last_index=$(tail -2 em.gro | head -1 | cut -c16-20 | tr -d ' ')
cat << EOF | gmx_mpi make_ndx -f em.gro -o index.ndx
a 1-38291
name 17 pro
a {PEPTIDE_START}-$last_index
name 18 chainM
q
EOF

gmx_mpi grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -n index.ndx
gmx_mpi mdrun -deffnm nvt -v
gmx_mpi grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -n index.ndx
gmx_mpi mdrun -deffnm npt -v
gmx_mpi grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr -n index.ndx -r npt.gro
gmx_mpi mdrun -v -deffnm md
"""

    try:
        subprocess.run(f'bash -i -c "{bash_script}"', shell=True, check=True, env=env)
        print(f"✅ ：{pdb_name} on GPU {gpu_id}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ：{pdb_name}， {e.returncode}")

def worker(args):
    pdb_path, gpu_id = args
    try:
        run_pipeline(pdb_path, gpu_id)
    except Exception as e:
        print(f"❌ ：{pdb_path}, GPU: {gpu_id}, : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpus', type=int, default=1, help=' GPU number（eg --gpus 2）')
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    pdb_list = [os.path.join(PDB_DIR, f) for f in os.listdir(PDB_DIR) if f.endswith(".pdb")]
    task_args = [(pdb_path, i % args.gpus) for i, pdb_path in enumerate(pdb_list)]

    pool = multiprocessing.Pool(processes=args.gpus)
    pool.map(worker, task_args)
    pool.close()
    pool.join()

    print("🎉 finish！")
