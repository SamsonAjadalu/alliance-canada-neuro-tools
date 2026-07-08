# Oppni B — parallel fMRI preprocessing

Oppni B on Alliance clusters: one Slurm job per input row.

## Prerequisites

- [docs/setup.md](../../docs/setup.md) — modules, AFNI, MATLAB
- Oppni and dependencies cloned on `$SCRATCH`
- BIDS-style paths in your real `input_auto.txt` (on scratch, not in git)

## Setup on scratch

```bash
export PROJECT_DIR=$SCRATCH/my_project
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# From this repo — copy examples and rename (drop .example)
cp tools/oppni-b/config.m.example       config.m
cp tools/oppni-b/pipeline1.txt.example  pipeline1.txt
cp tools/oppni-b/paramfile.txt.example  paramfile.txt
cp tools/oppni-b/input_auto.txt.example input_auto.txt

# Edit config.m: set addpath() to your oppni-code-nwc and neuro-code-nwc locations
# Edit input_auto.txt: real PREFIX, ANAT, FUNC paths
```

## Generate sbatch files

```bash
python3 create_jobs.py --pipeline pipeline1.txt
# writes one slurm_tickets_<PNAME>/*.sl per line in input_auto.txt, plus master_slurm_<PNAME>.sh
```

Or submit manually using [example_sbatch.sl](example_sbatch.sl) as a template. The last number in `P2_fmri_dataProcessing(..., ROW)` must match the row in `input_auto.txt`.

## Pass 1 — per-subject preprocessing

Submit one job per subject. Each job runs heavy anat/func work for that row only.

```bash
sbatch slurm_tickets_<PNAME>/sub-EXAMPLE_ses-1_sbatch.sl
```

If the log ends with `not all subjects processed enough to mask. Halting for now!` — that subject likely finished stage 1; wait until **all** subjects in `input_auto.txt` have completed before pass 2.

## Pass 2 — group masks and func part 2

When every subject in `input_auto.txt` has finished func part 1, re-submit the same jobs (or `master_slurm_<PNAME>.sh`).

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `Unable to read MAT-file` on `pipe_key.mat` | Check that no stale or partial `pipe_key.mat` exists before rerunning |
| `subject_list_formask` / corrupt `mask_subj_idxes.mat` | Re-run after all pass-1 subjects finish; remove stale group-level files only if no jobs are running |
| Jobs hang at Step-0 | `rm -rf fmri_proc/_pipe_manager/.pipe_key_lock` (no jobs running) |
| Jobs hang at P2 startup | `rm -rf fmri_proc/_group_level/.mask_subj_idxes_lock_pipe_Base1` (adjust `Base1` to your `PNAME`) |
| Jobs hang in `roimask_OP1` | `rm -rf fmri_proc/_group_level/.roimask_lock_pipe_Base1` |
| `libGLw.so.1` | Use cluster AFNI in [setup.md](../../docs/setup.md) |
| `Halting for now!` | Normal on pass 1 if other subjects not ready |
| Changing subject list for group mask | Remove `fmri_proc/_group_level/` per Oppni docs |
