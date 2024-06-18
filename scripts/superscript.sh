#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --partition={work_queue}
#SBATCH --reservation={given reservation}
#SBATCH --job-name=superJob
#SBATCH --nodes=1 # Total number of nodes
#SBATCH --ntasks=1 # Total number of MPI tasks
#SBATCH --cpus-per-task=8 # CPU cores per MPI task
#SBATCH --mem=1G
#SBATCH --time=00:01:00

cd /scratch/${PAWSEY_PROJECT}/${USER}

# Run hostname just because
hostname

# Make an empty file
touch run.txt 

# Don't actually run anything, replace this with actual work
echo srun toolName arguments
