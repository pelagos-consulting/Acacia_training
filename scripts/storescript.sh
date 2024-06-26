#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --job-name=storeTar
#SBATCH --partition=copy
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --export=NONE

module load rclone/{rclone_version}

# Store files to Acacia

# Streaming approach
cd {scratchDir}
srun tar cf - . --use-compress-program="pigz" | rclone rcat -q {acaciaAlias}:{acaciaOutPath}
