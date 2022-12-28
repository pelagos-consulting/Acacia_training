#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --job-name=stageTar
#SBATCH --partition={copy_queue}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --export=NONE

# You may have to change these module load commands
module load rclone/{rclone_version}

# Stage files from Acacia

# Streaming approach
srun mkdir -p {scratchDir}
srun rclone cat {acaciaAlias}:{acaciaInPath} | tar xf - --directory {scratchDir}/ --use-compress-program="pigz"
