#!/usr/bin/env python3
"""Generate Slurm tickets for an OPPNI P2 run."""

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


def absolute_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def matlab_string(path: str) -> str:
    return path.replace("'", "''")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create OPPNI Slurm job tickets")
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory for generated tickets, logs, master script, and OPPNI output",
    )
    parser.add_argument("--input", default="input_auto.txt", help="Input file path")
    parser.add_argument("--pipeline", required=True, help="Pipeline file path")
    parser.add_argument("--param", default="paramfile.txt", help="Parameter file path")
    parser.add_argument("--config", default="config.m", help="MATLAB config.m path")
    parser.add_argument("--account", default="def-nwc")
    parser.add_argument("--time", default="0-05:00:00")
    parser.add_argument("--cpus", type=int, default=4)
    parser.add_argument("--mem", default="64G")
    args = parser.parse_args()

    output_dir = absolute_path(args.output_dir)
    input_path = absolute_path(args.input)
    pipeline_path = absolute_path(args.pipeline)
    param_path = absolute_path(args.param)
    config_path = absolute_path(args.config)

    for label, path in (("pipeline", pipeline_path), ("input", input_path),
                        ("param", param_path), ("config", config_path)):
        if not os.path.isfile(path):
            sys.exit(f"ERROR: missing {label} file: {path}")
    if args.cpus < 1:
        sys.exit("ERROR: --cpus must be at least 1")

    pname = parse_pname(pipeline_path)
    ticket_folder = os.path.join(output_dir, f"slurm_tickets_{pname}")
    log_folder = os.path.join(output_dir, "slurm_logs")
    os.makedirs(ticket_folder, exist_ok=True)
    os.makedirs(log_folder, exist_ok=True)

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    master_path = os.path.join(output_dir, f"master_slurm_{pname}.sh")
    prefixes = set()
    with open(master_path, "w") as master_file:
        master_file.write("#!/bin/bash\nset -euo pipefail\n")
        for row, line in enumerate(lines, start=1):
            match = re.search(r"PREFIX=([^\s]+)", line)
            if not match:
                sys.exit(f"ERROR: input line {row} has no PREFIX= field")
            prefix = match.group(1)
            if prefix in prefixes:
                sys.exit(f"ERROR: duplicate PREFIX={prefix} on input line {row}")
            prefixes.add(prefix)

            filename = f"{prefix}_sbatch.sl"
            filepath = os.path.join(ticket_folder, filename)
            with open(filepath, "w") as job_file:
                job_file.write("#!/bin/bash -l\n")
                job_file.write(f"#SBATCH --job-name={prefix}_{pname}\n")
                job_file.write(f"#SBATCH --account={args.account}\n")
                job_file.write(f"#SBATCH --time={args.time}\n")
                job_file.write("#SBATCH --ntasks=1\n#SBATCH --nodes=1\n")
                job_file.write(f"#SBATCH --cpus-per-task={args.cpus}\n")
                job_file.write(f"#SBATCH --mem={args.mem}\n")
                job_file.write(f"#SBATCH --output={log_folder}/%x_%j.out\n\n")
                job_file.write(f"cd '{output_dir}'\n\n")
                matlab_cmd = (
                    "matlab -nodisplay -nojvm -singleCompThread -r "
                    f"\"run('{matlab_string(config_path)}'); "
                    f"P2_fmri_dataProcessing('{matlab_string(input_path)}', "
                    f"'{matlab_string(pipeline_path)}', '{matlab_string(param_path)}', "
                    f"'{matlab_string(output_dir)}', 0, [], {row}); exit;\"\n"
                )
                job_file.write(matlab_cmd)
            master_file.write(f"sbatch '{filepath}'\n")

    os.chmod(master_path, 0o755)
    print(f"Done. PNAME={pname}")
    print(f"  {master_path}")
    print(f"  {len(lines)} jobs in {ticket_folder}/")


if __name__ == "__main__":
    main()
