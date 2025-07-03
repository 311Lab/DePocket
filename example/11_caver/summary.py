import os
import csv

# Define the output directory path
output_dir = './output'

# Define the path for the summary CSV file
summary_csv = 'summary_tunnel_characteristics.csv'

# Open or create the summary CSV file
with open(summary_csv, mode='w', newline='') as summary_file:
    writer = csv.writer(summary_file)

    # Iterate over each folder in the output directory
    for pdb_name in os.listdir(output_dir):
        pdb_folder = os.path.join(output_dir, pdb_name)

        # Ensure it's a directory
        if os.path.isdir(pdb_folder):
            tunnel_csv_path = os.path.join(pdb_folder, 'analysis', 'tunnel_characteristics.csv')

            # Check if the tunnel_characteristics.csv file exists
            if os.path.exists(tunnel_csv_path):
                with open(tunnel_csv_path, mode='r') as tunnel_file:
                    reader = csv.reader(tunnel_file)
                    # Read the first row as header
                    header = next(reader)

                    # If the summary file is empty (i.e., first write), write the header
                    if summary_file.tell() == 0:
                        writer.writerow(['PDB Name'] + header)  # Add PDB Name column as an identifier

                    # Read the channel information (second row) and prepend the PDB folder name as the first column
                    channel_info = next(reader)
                    writer.writerow([pdb_name] + channel_info)
            else:
                print(f"Warning: {tunnel_csv_path} does not exist")
                
print(f"Summary completed. Output file: {summary_csv}")
