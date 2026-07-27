#!/usr/bin/env python3
"""Generate Slurm tickets for an Oppni D P1 run."""

import argparse
import os
import re
import sys


def resolve_path(base_dir: str, path: str) -> str:
    if os.path.isabs(path):
        return os.path.abspath(path)

    return os.path.abspath(os.path.join(base_dir, path))


def matlab_quote(path: str) -> str:
    return path.replace("'", "''")


def clean_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Oppni D Slurm job tickets")
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Project root for Slurm files",
    )
    parser.add_argument("--input", default="input_file_diff.txt", help="Diffusion input file")
    parser.add_argument("--out-dir", default=None, help="Output directory passed to MATLAB")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    input_path = resolve_path(base_dir, args.input)
    out_dir = resolve_path(base_dir, args.out_dir) if args.out_dir else base_dir

    if not os.path.isfile(input_path):
        sys.exit(f"ERROR: missing {input_path}")

    ticket_folder = os.path.join(base_dir, "slurm_tickets_diff")
    os.makedirs(ticket_folder, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "slurm_logs"), exist_ok=True)

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    master_path = os.path.join(base_dir, "master_slurm_diff.sh")
    job_count = 0

    with open(master_path, "w") as master_file:
        master_file.write("#!/bin/bash\n")
        for v, line in enumerate(lines, start=1):
            match = re.search(r"PREFIX=\[?([^\]\s]+)\]?", line)
            if not match:
                continue

            prfix = clean_name(match.group(1))
            filename = f"{prfix}_sbatch.sl"
            filepath = os.path.join(ticket_folder, filename)

            with open(filepath, "w") as job_file:
                job_file.write("#!/bin/bash -l\n")
                job_file.write(f"#SBATCH --job-name={prfix}_diff\n")
                job_file.write("#SBATCH --account=def-nwc\n")
                job_file.write("#SBATCH --time=0-05:00:00\n")
                job_file.write("#SBATCH --ntasks=1\n")
                job_file.write("#SBATCH --nodes=1\n")
                job_file.write("#SBATCH --cpus-per-task=4\n")
                job_file.write("#SBATCH --mem=64G\n")
                job_file.write(f"#SBATCH --output={base_dir}/slurm_logs/%x_%j.out\n\n")
                job_file.write('export MATLAB_PREFDIR="$SLURM_TMPDIR/matlab_pref"\n')
                job_file.write('mkdir -p "$MATLAB_PREFDIR"\n')
                job_file.write("export OPPNI_NODDI=OFF\n")
                job_file.write("export OPPNI_DIFF_WARP=ON\n\n")

                matlab_cmd = (
                    f"matlab -nodisplay -nojvm -singleCompThread -r "
                    f"\"config; P1_diff_dataProcessing('{matlab_quote(input_path)}', "
                    f"'{matlab_quote(out_dir)}', 0, {v}); exit;\"\n"
                )
                job_file.write(matlab_cmd)

            master_file.write(f"sbatch slurm_tickets_diff/{filename}\n")
            job_count += 1

    if job_count == 0:
        sys.exit(f"ERROR: no PREFIX= rows found in {input_path}")

    print("Done. Oppni D")
    print(f"  {master_path}")
    print(f"  {job_count} jobs in {ticket_folder}/")


if __name__ == "__main__":
    main()
