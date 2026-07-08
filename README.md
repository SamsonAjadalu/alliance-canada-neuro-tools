# alliance-canada-neuro-tools

Runbooks and templates for neuroimaging pipelines on [Digital Research Alliance of Canada](https://alliancecan.ca/) clusters (e.g. Narval).

## Contents

| Path | Description |
|------|-------------|
| [docs/setup.md](docs/setup.md) | Modules, environment, `bash_profile` |
| [docs/slurm.md](docs/slurm.md) | Submitting and monitoring jobs |
| [narval/](narval/) | Narval shell setup examples and AFNI `count_afni` wrapper |
| [shared/](shared/) | Example `bash_profile` and sbatch template |
| [tools/oppni-b/](tools/oppni-b/) | Oppni B (fMRI) parallel workflow |
| [tools/oppni-d/](tools/oppni-d/) | Placeholder |
| [tools/oppni-a/](tools/oppni-a/) | Placeholder |

## Quick start

1. Read [docs/setup.md](docs/setup.md) and configure your login environment.
2. Pick a tool under `tools/` and follow its `README.md`.
3. Keep real data and outputs on `$SCRATCH` — not in this repo.

## Adding a new tool

Create `tools/<name>/README.md` plus any example configs. Keep study-specific files as `*.example` or on scratch only.
