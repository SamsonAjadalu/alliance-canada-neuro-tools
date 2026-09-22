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
python3 /path/to/alliance-canada-neuro-tools/tools/oppni-b/create_jobs.py \
  --output-dir "$PROJECT_DIR" \
  --input "$PROJECT_DIR/input_auto.txt" \
  --pipeline "$PROJECT_DIR/pipeline1.txt" \
  --param "$PROJECT_DIR/paramfile.txt" \
  --config "$PROJECT_DIR/config.m" \
  --time 0-05:00:00 --mem 32G --cpus 4
# writes slurm_tickets_<PNAME>/*.sl, slurm_logs/, and master_slurm_<PNAME>.sh
```

All input, pipeline, parameter, and config paths are resolved to absolute paths,
so those files may live anywhere. `--output-dir` is used only for generated
tickets, logs, the master script, and the OPPNI output directory; it replaces
the old `--base-dir` option. The generator checks that all four files exist,
rejects missing or duplicate `PREFIX` values, and runs the supplied `config.m`
by its absolute path. Resource options are configurable with `--account`,
`--time`, `--mem`, and `--cpus`.

For files in the current directory, use their names directly; do not repeat
the output directory in the file argument:

```bash
python3 /path/to/create_jobs.py --output-dir "$PROJECT_DIR" \
  --input input_auto.txt --pipeline pipeline1.txt \
  --param paramfile.txt --config config.m
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
