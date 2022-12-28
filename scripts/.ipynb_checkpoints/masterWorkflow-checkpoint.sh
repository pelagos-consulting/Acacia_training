#!/bin/bash

# Master script to control your Pawsey workflow

# Run the staging script, there is no prior dependency
stageJobID=$(sbatch --parsable stagescript.sh | cut -d ' ' -f 1)

# Now the supercomputing script, depend on staging
superJobID=$(sbatch --dependency=afterok:$stageJobID --parsable superscript.sh | cut -d ' ' -f 1)

# And the storage script, depend on supercomputing
storeJobID=$(sbatch --dependency=afterok:$superJobID --parsable storescript.sh | cut -d ' ' -f 1)

# Check the queues to see how we are going
squeue --me
