import shutil
import pandas as pd
import os

def create_initial_score_file(input_file, output_file, pdb_folder):
    """
    Simply copy the input file to output file (effectively renaming it),
    then remove rows where the value in the 7th column (index 6) is greater than -1.5.
    Also, delete PDB files in 'scored_pdbs' folder that are not in the filtered CSV.
    """
    if os.path.exists(input_file): 
        # Step 1: Copy the entire input file to output file (rename)
        shutil.copy(input_file, output_file)

        # Step 2: Read the copied file, skipping the first row (header)
        df = pd.read_csv(output_file, header=None, skiprows=1, usecols=range(22), on_bad_lines='skip')  # Skip first row and only read the first 22 columns

        # Step 3: Filter rows where the value in the 7th column (index 6) is less than or equal to -1.5
        df = df[df.iloc[:, 7] <= -1.5]  # Directly filter rows based on the 7th column value

        # Step 4: Overwrite the output file with the filtered data
        df.to_csv(output_file, index=False, header=False)  # Don't include index or header

        # Step 5: Delete PDB files in 'scored_pdbs' folder that are not in the filtered CSV
        descriptions = set(df.iloc[:, 0])  # Assuming 'description' is in the first column (index 0)
        for filename in os.listdir(pdb_folder):
            if filename.endswith('.pdb'):
                base_name = filename[:-4]  # Remove the '.pdb' suffix
                # Check if the base_name (without .pdb) contains any description value
                if not any(desc in base_name for desc in descriptions):  # If description is not part of the PDB filename
                    file_path = os.path.join(pdb_folder, filename)
                    os.remove(file_path)  # Delete the file
    else:
        raise FileNotFoundError(f"{input_file} not found, cannot create {output_file}")

def main():
    input_file = 'interface_analysis_summary.csv'
    csv_file = 'score_1.5.csv'
    pdb_folder = 'scored_pdbs'

    # Create the initial filtered file by copying and processing
    create_initial_score_file(input_file, csv_file, pdb_folder)

if __name__ == '__main__':
    main()
