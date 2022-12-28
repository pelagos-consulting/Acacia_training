#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --partition={debug_queue}
#SBATCH --job-name=superJob
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --export=NONE

cd {scratchDir}

# Run hostname just because
hostname

# Make an empty file
touch run.txt 

# Don't actually run anything
echo srun toolName arguments
