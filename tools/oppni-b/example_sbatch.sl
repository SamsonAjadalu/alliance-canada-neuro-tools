#!/bin/bash -l
#SBATCH --job-name=sub-EXAMPLE_ses-1_sbatch
#SBATCH --account=def-YOUR_ALLOC
#SBATCH --time=0-05:00:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G

export PROJECT_DIR=${PROJECT_DIR:-$SCRATCH/my_project}
cd "$PROJECT_DIR"

matlab -nodisplay -nojvm -singleCompThread -r "config; P2_fmri_dataProcessing(fullfile(getenv('PROJECT_DIR'),'input_auto.txt'), fullfile(getenv('PROJECT_DIR'),'pipeline1.txt'), fullfile(getenv('PROJECT_DIR'),'paramfile.txt'), getenv('PROJECT_DIR'), 0, [], 1); exit;"
