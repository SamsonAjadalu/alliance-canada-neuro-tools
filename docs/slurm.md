# Slurm basics

## Submit and monitor

```bash
sbatch myjob.sl
squeue --user=$USER
sacct -j JOBID --format=JobID,JobName,State,ExitCode,Elapsed
scancel JOBID
```

## Sbatch template

See [shared/sbatch.template.sl](../shared/sbatch.template.sl). Use `#!/bin/bash -l` so modules from your profile load.

## One job per subject (Oppni pattern)

- One row in `input_auto.txt` = one subject/session
- Last argument to `P2_fmri_dataProcessing(..., row_index)` selects that row
- Many jobs can run in parallel on different nodes

## Two-pass workflow (when a checkpoint exists)

Some pipelines need every subject to finish stage 1 before group-level steps:

| Pass | What happens |
|------|----------------|
| **Pass 1** | Each job runs heavy per-subject preprocessing; may exit at a checkpoint if others are not ready |
| **Pass 2** | Re-submit the same jobs after all subjects complete stage 1; group masks and later steps run |

`COMPLETED` with exit code `0` does not always mean the full pipeline finished — read the log.

## Parallel writes to one file

If many jobs update the same file at startup, use a filesystem lock (see Oppni B P0 patch) or serialize that step. Staggering `sbatch` submit time does **not** control when Slurm starts jobs after queue wait.
