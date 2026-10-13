#!/bin/bash
#SBATCH -J ford_sweep
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p gh
#SBATCH -t 04:00:00
#SBATCH -A BCS20003
#SBATCH -o ford_sweep_%j.out
#SBATCH -e ford_sweep_%j.err

set -e
cd $STOCKYARD/vista/can-it-ford
source $STOCKYARD/vista/.venv/bin/activate
python $STOCKYARD/vista/can-it-ford/scripts/ford_sweep_driver.py
