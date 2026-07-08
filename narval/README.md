# Narval Environment

Example shell setup for running these tools on Narval.

Use `bash_profile.example` and `bashrc.example` as references. Do not overwrite an existing shell setup without checking it first.

## Modules

`bash_profile.example` loads:

- `StdEnv/2023`
- `gcc/12.3`
- `matlab/2023b.2`
- `python/3.10.13`
- `ants/2.6.5`
- `fsl/6.0.7.20`

AFNI is added directly through its CVMFS binary path:

```bash
/cvmfs/soft.computecanada.ca/easybuild/software/2023/x86-64-v3/Compiler/gcc12/afni/26.0.09/bin
```

Do not `module load afni` for this setup; it can pull a conflicting Python version.

## count_afni

Some AFNI-generated scripts call `count_afni`, but this Narval AFNI install provides `count`.

Put the included `count_afni` wrapper somewhere on `PATH`, usually:

```bash
~/bin/count_afni
```

`bashrc.example` adds `~/bin` and `~/.local/bin` to `PATH`.
