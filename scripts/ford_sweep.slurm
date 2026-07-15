#!/bin/bash
#SBATCH -J ford_sweep
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p gh
#SBATCH -t 04:00:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/logs/ford_sweep_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/logs/ford_sweep_%j.err

set -e
cd /work/11603/jcerrell0629/vista/can-it-ford
source /work/11603/jcerrell0629/vista/.venv/bin/activate
python /work/11603/jcerrell0629/vista/can-it-ford/scripts/ford_sweep_driver.py
