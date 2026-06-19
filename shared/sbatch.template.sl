#!/bin/bash -l
#SBATCH --job-name=example_job
#SBATCH --account=def-YOUR_ALLOC
#SBATCH --time=0-05:00:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G

# Your command here (MATLAB, Python, etc.)
# matlab -nodisplay -nojvm -batch "disp('hello');"
