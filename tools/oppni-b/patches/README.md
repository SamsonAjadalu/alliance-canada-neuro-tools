# Oppni B patches for parallel jobs

Full-file replacements for stock Oppni B. Copy over your install under `oppni-code-nwc/oppni-b/`.

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

Apply **both** patches if you run many parallel P2 jobs on a shared filesystem (e.g. Lustre).
