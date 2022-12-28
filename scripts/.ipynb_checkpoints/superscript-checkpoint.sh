#!/bin/bash --login
#SBATCH --account=courses01
#SBATCH --partition=debuq
#SBATCH --job-name=superJob
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --export=NONE

cd /scratch/courses01/cou001/working

# Run hostname just because
hostname

# Make an empty file
touch run.txt 

# Don't actually run anything
echo srun toolName arguments
