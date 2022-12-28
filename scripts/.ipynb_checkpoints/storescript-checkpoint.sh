#!/bin/bash --login
#SBATCH --account=courses01
#SBATCH --job-name=storeTar
#SBATCH --partition=copyq
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --export=NONE

module load rclone/1.58.1

# Store files to Acacia

# Streaming approach
cd /scratch/courses01/cou001/working
srun tar cf - . --use-compress-program="pigz" | rclone rcat -q acacia-mine:courses01-acacia-tmp/simulation_out.tar.gz
