# Oppni B patches for parallel jobs

Full-file replacements for stock Oppni. Copy over your install.

## P0 — `pipe_key.mat`

```bash
cp patches/P0_fmri_populateDirectories.m \
   $SCRATCH/path/to/oppni-code-nwc/oppni-b/P0_fmri_populateDirectories.m
```

Shell `mkdir` lock around the `pipe_key.mat` read/write block (Step-0 / P0).

Stale lock: `rm -rf fmri_proc/_pipe_manager/.pipe_key_lock`

## P2 — `pipe_*_mask_subj_idxes.mat`

```bash
cp patches/P2_fmri_dataProcessing.m \
   $SCRATCH/path/to/oppni-code-nwc/oppni-b/P2_fmri_dataProcessing.m
```

Shell `mkdir` lock around load/save of `fmri_proc/_group_level/pipe_<PNAME>_mask_subj_idxes.mat` at P2 startup.

Stale lock (example for pipeline `Base1`):

```bash
rm -rf fmri_proc/_group_level/.mask_subj_idxes_lock_pipe_Base1
```

## roimask_OP1 — group binary masks (CSF / WM / GM / tSD)

```bash
cp patches/roimask_OP1.m \
   $SCRATCH/path/to/oppni-code-nwc/oppni-x/shared/roimask_OP1.m
```

At pass 2, every job calls `roimask_OP1`. Stock code rewrote `func_tSD_mask_grp.nii` on every job.

Patch:

1. **tSD `if exist` / `else save`** (same as CSF, WM, GM)
2. **Shell `mkdir` lock** around the whole mask block — one job builds all four masks, others wait then verify

Stale lock (example for pipeline `Base1`):

```bash
rm -rf fmri_proc/_group_level/.roimask_lock_pipe_Base1
```

Apply **all three** patches for many parallel P2 jobs on Lustre.
