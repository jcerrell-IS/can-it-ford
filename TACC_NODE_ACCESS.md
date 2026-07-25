# TACC Node Access Reference

Vista and LS6 idev commands, diagnostics, and cancel commands. Verified against TACC's live docs July 24 2026.

## Vista

ssh jcerrell0629@vista.tacc.utexas.edu

Default GPU dev queue, usual session:
```
idev -p gh-dev -N 1 -n 1 -t 2:00:00
```

Production GPU, long run:
```
idev -p gh -N 1 -n 1 -t 24:00:00
```

CPU-only, no GPU needed:
```
idev -p gg -N 1 -n 1 -t 1:00:00
```

After landing, activate the right environment:
- Genesis/MPM (Track 2): `module load tacc-apptainer && export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif`
- kks32/mpm-engine (Track 1): activate `mpmenv`
- General Python/file work: plain `python3`, no container

## LS6

ssh jcerrell0629@ls6.tacc.utexas.edu

GPU dev queue, usual session:
```
idev -p gpu-a100-dev -N 1 -n 1 -t 2:00:00
```

Production A100, long run:
```
idev -p gpu-a100 -N 1 -n 1 -t 24:00:00
```

Fractional A100, light testing:
```
idev -p gpu-a100-small -N 1 -n 1 -t 1:00:00
```

CPU-only, quick check:
```
idev -p development -N 1 -n 1 -t 0:30:00
```

CPU-only, production up to 48h:
```
idev -p normal -N 1 -n 1 -t 12:00:00
```

## Before requesting a node

```
squeue -u jcerrell0629
sinfo -S+P -o "%P %F"
```

First checks whether a job of yours is already blocking a new dev-queue request. Second checks idle node counts per partition.

## Will it load, and how long

```
sinfo -p gh-dev -o "%20P %5D %6t"
squeue -p gh-dev -t PD
squeue --start -j JOBID
scontrol show job JOBID
qlimits
showq
```

`qlimits` is the most current source, more current than any written table, including this one.

## Cancel a job

```
scancel JOBID
scancel -u jcerrell0629
scancel -u jcerrell0629 -p gh-dev
```

## Notes

Dev queues cap you near one active job at a time. Always run `squeue -u jcerrell0629` before assuming the cluster itself is slow, it might be your own old session sitting there.

SLURM uses fair-share priority, not first-come-first-served. `squeue -t PD` row count is a rough signal, not a guarantee.

48 hours is TACC's hard system-wide max on normal-tier queues, no exceptions, no extensions.
