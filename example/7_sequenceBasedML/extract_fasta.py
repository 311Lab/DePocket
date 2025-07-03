# -*- coding: utf-8 -*-  
print("Script started")
import os
import glob
import re  

def extract_number(filename):
    
    match = re.findall(r'\d+', os.path.basename(filename))
    return int(match[-1]) if match else 0  

def extract_and_merge_fasta(input_dir, output_file):
    
    fasta_files = glob.glob(os.path.join(input_dir, "*.fa"))
    
   
    fasta_files.sort(key=extract_number)
    print("Sorted files:", [os.path.basename(f) for f in fasta_files])  
    
    print(f"Found {len(fasta_files)} FASTA files.")

    with open(output_file, "w") as out_f:
        for file_path in fasta_files:
            print(f"Processing file: {file_path}")
            with open(file_path, "r") as in_f:
                lines = in_f.readlines()[2:]  
                
                current_id = ""
                current_seq = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith(">"):
                        if current_id:  
                            out_f.write(f"{current_id}\n{''.join(current_seq)}\n\n")
                        current_id = line
                        current_seq = []
                    else:
                        current_seq.append(line)
                
               
                if current_id:
                    out_f.write(f"{current_id}\n{''.join(current_seq)}\n\n")
                    print(f"Written: {current_id[:50]}...") 


    print(f"Output written to {output_file}")

if __name__ == "__main__":
    input_directory = "../../../ProteinMPNN-main/outputs/example_2_outputs/seqs"
    output_file = "../7_sequenceBasedML/combined.fasta"
    extract_and_merge_fasta(input_directory, output_file)