# -*- coding: utf-8 -*-

import os
import subprocess

def run_sbatch():
    
    os.chdir('../../../ProteinMPNN-main/examples')

    
    subprocess.run('bash -i -c "conda activate mlfold && sbatch submit_example_2.sh"', shell=True, check=True)

if __name__ == "__main__":
    try:
        run_sbatch()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
