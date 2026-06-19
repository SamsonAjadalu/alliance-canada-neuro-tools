import os
import re

# Set before running, or edit defaults below:
#   export PROJECT_DIR=$SCRATCH/my_project
PROJECT_DIR = os.environ.get("PROJECT_DIR", os.path.join(os.environ.get("SCRATCH", "/scratch"), "my_project"))

input_file_path = os.path.join(PROJECT_DIR, "input_auto.txt")
out_dir = PROJECT_DIR

f_dir = PROJECT_DIR
in_name = "input_auto.txt"
pipe_name = "pipeline1.txt"
param_name = "paramfile.txt"

ticket_folder = os.path.join(PROJECT_DIR, "slurm_tickets")
os.makedirs(ticket_folder, exist_ok=True)

with open(input_file_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

with open(os.path.join(PROJECT_DIR, "master_slurm.sh"), "w") as master_file:
    for v, line in enumerate(lines, start=1):
        match = re.search(r"PREFIX=([^\s]+)", line)
        if not match:
            continue

        prfix = match.group(1)
        filename = f"{prfix}_sbatch.sl"
        filepath = os.path.join(ticket_folder, filename)

        with open(filepath, "w") as job_file:
            job_file.write("#!/bin/bash -l\n")
            job_file.write(f"#SBATCH --job-name={prfix}_sbatch\n")
            job_file.write("#SBATCH --account=def-YOUR_ALLOC\n")
            job_file.write("#SBATCH --time=0-05:00:00\n")
            job_file.write("#SBATCH --ntasks=1\n")
            job_file.write("#SBATCH --nodes=1\n")
            job_file.write("#SBATCH --cpus-per-task=4\n")
            job_file.write("#SBATCH --mem=64G\n\n")

            matlab_cmd = (
                f"matlab -nodisplay -nojvm -singleCompThread -r "
                f"\"config; P2_fmri_dataProcessing(fullfile('{f_dir}','{in_name}'), "
                f"fullfile('{f_dir}','{pipe_name}'), fullfile('{f_dir}','{param_name}'), "
                f"'{out_dir}', 0, [], {v}); exit;\"\n"
            )
            job_file.write(matlab_cmd)

        master_file.write(f"sbatch {ticket_folder}/{filename}\n")

print(f"Done. Created master_slurm.sh and {len(lines)} SLURM files in {ticket_folder}/")
