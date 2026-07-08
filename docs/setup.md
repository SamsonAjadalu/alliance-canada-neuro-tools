# Cluster setup (Narval)

## Scratch and project layout

```bash
echo $SCRATCH          # e.g. /scratch/$USER or /lustre07/scratch/$USER
mkdir -p $SCRATCH/my_project
```

Keep BIDS input, Oppni outputs (`fmri_proc/`), and Slurm logs on scratch — not in git.

## Modules (login shell)

Sbatch scripts should start with `#!/bin/bash -l` so your profile loads.

Example — see [shared/bash_profile.example](../shared/bash_profile.example):

```bash
module load StdEnv/2023 gcc/12.3 matlab/2023b.2 python/3.10.13
module load ants/2.6.5 fsl/6.0.7.20
export PATH="/cvmfs/soft.computecanada.ca/easybuild/software/2023/x86-64-v3/Compiler/gcc12/afni/24.1.03/bin:${PATH}"
```

## AFNI on Alliance clusters

Use the **EasyBuild cluster AFNI** via `PATH` (above). In MATLAB, set the same path in `config.m` (see `tools/oppni-b/config.m.example`).

### Do not

- `module load afni` together with ANTs without resolving Python version conflicts
- Set `LD_LIBRARY_PATH` to custom Rocky/Gentoo AFNI builds (can segfault MATLAB)
- Point `PATH` at a personal Rocky AFNI tree missing `libGLw.so.1` on compute nodes

## Oppni / neuro code

Clone Oppni and dependencies on scratch, then point `config.m` at those paths.

## Verify environment

```bash
which matlab
which 3dAllineate
which antsRegistration
module list
```
