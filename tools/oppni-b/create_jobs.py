#!/usr/bin/env python3
"""Generate Slurm tickets for an Oppni P2 run. Ticket folder and master script use PNAME."""

import argparse
import os
import re
import sys


def parse_pname(pipeline_path: str) -> str:
    with open(pipeline_path, "r") as f:
        for line in f:
            m = re.search(r"PNAME=\[([^\]]+)\]", line.strip())
            if m:
                return m.group(1)

    sys.exit(f"ERROR: no PNAME= in {pipeline_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Oppni Slurm job tickets")
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Project root (outpath passed to MATLAB)",
    )
    parser.add_argument("--input", default="input_auto.txt", help="Input file name")
    parser.add_argument("--pipeline", required=True, help="Pipeline file name")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    pipeline_name = args.pipeline
    pipeline_path = os.path.join(base_dir, pipeline_name)
    input_name = args.input
    input_path = os.path.join(base_dir, input_name)
    param_name = "paramfile.txt"

    if not os.path.isfile(pipeline_path):
        sys.exit(f"ERROR: missing {pipeline_path}")
    if not os.path.isfile(input_path):
        sys.exit(f"ERROR: missing {input_path}")

    pname = parse_pname(pipeline_path)
    ticket_folder = os.path.join(base_dir, f"slurm_tickets_{pname}")
    os.makedirs(ticket_folder, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "slurm_logs"), exist_ok=True)

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    master_path = os.path.join(base_dir, f"master_slurm_{pname}.sh")
    with open(master_path, "w") as master_file:
        master_file.write("#!/bin/bash\n")
        for v, line in enumerate(lines, start=1):
            match = re.search(r"PREFIX=([^\s]+)", line)
            if not match:
                continue

            prfix = match.group(1)
            filename = f"{prfix}_sbatch.sl"
            filepath = os.path.join(ticket_folder, filename)

            with open(filepath, "w") as job_file:
                job_file.write("#!/bin/bash -l\n")
                job_file.write(f"#SBATCH --job-name={prfix}_{pname}\n")
                job_file.write("#SBATCH --account=def-nwc\n")
                job_file.write("#SBATCH --time=0-05:00:00\n")
                job_file.write("#SBATCH --ntasks=1\n")
                job_file.write("#SBATCH --nodes=1\n")
                job_file.write("#SBATCH --cpus-per-task=4\n")
                job_file.write("#SBATCH --mem=64G\n")
                job_file.write(f"#SBATCH --output={base_dir}/slurm_logs/%x_%j.out\n\n")

                matlab_cmd = (
                    f"matlab -nodisplay -nojvm -singleCompThread -r "
                    f"\"config; P2_fmri_dataProcessing(fullfile('{base_dir}','{input_name}'), "
                    f"fullfile('{base_dir}','{pipeline_name}'), fullfile('{base_dir}','{param_name}'), "
                    f"'{base_dir}', 0, [], {v}); exit;\"\n"
                )
                job_file.write(matlab_cmd)

            master_file.write(f"sbatch slurm_tickets_{pname}/{filename}\n")

    print(f"Done. PNAME={pname}")
    print(f"  {master_path}")
    print(f"  {len(lines)} jobs in {ticket_folder}/")


if __name__ == "__main__":
    main()
