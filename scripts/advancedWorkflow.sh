#!/bin/bash 

# The project you want to charge to
account=${PAWSEY_PROJECT}

# ID for this run, use local time zone for now
dateTime=$(date +%Y%m%d-LOCAL-%H-%M-%S)

# Your alias for interacting with Acacia
acaciaAlias=acacia-mine

# Your chosen bucket name (must edit this)
BucketName=courses01-acacia-tmp

# Set copy_queue and debug_queue and rclone version
copy_queue=copy
debug_queue=debug
rclone_version=1.63.1

# Path to get files from Acacia, comment out or leave blank (AcaciaInPath=) for no staging 
acaciaInPath=${BucketName}/simulation.tar.gz

# Path to put files on Acacia, comment out or leave blank (AcaciaOutPath=) for no storing
acaciaOutPath=${BucketName}/simulation-${dateTime}.tar.gz

# Path in scratch to work from
scratchDir=/scratch/${account}/${USER}/work

# Do we actually run the super job?
# Comment out or leave blank (runSuper=) for no super job
runSuper=yes

# Store the stage-in script in a variable called stageScript,
# edit these scripts for your own use.

# Anything that BASH considers as special characters, such as dollar signs and backslashes
# will be evaluated straight away (before sbatch can run it),
# So if you want these characters to persist into the job script they
# Must be escaped (e.g \\ or \$)

stageScript=$(cat <<EOF
#!/bin/bash --login
#SBATCH --account=${account}
#SBATCH --job-name=stageTar
#SBATCH --partition=${copy_queue}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=00:05:00

module load rclone/${rclone_version}

# Stage files from Acacia

# Streaming approach
srun mkdir -p ${scratchDir}
srun rclone cat ${acaciaAlias}:${acaciaInPath} -q | tar xf - --directory ${scratchDir}/ --use-compress-program="pigz"
EOF
)

# Store the job script in a variable called superScript
# edit this for your own use
superScript=$(cat <<EOF
#!/bin/bash --login
#SBATCH --account=${account}
#SBATCH --partition=${debug_queue}
#SBATCH --job-name=superJob
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:01:00

srun mkdir -p ${scratchDir}
cd ${scratchDir}
hostname

# Make an empty file
touch run-${dateTime}.txt

echo srun toolName arguments
EOF
) 

# Store the store script in a variable called storeScript
# edit this for your own use
storeScript=$(cat <<EOF
#!/bin/bash --login
#SBATCH --account=${account}
#SBATCH --job-name=storeTar
#SBATCH --partition=${copy_queue}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=00:05:00

module load rclone/${rclone_version}

# Store files to Acacia

# Simple streaming approach
# Use zcf or jcf for a compressed archive
cd ${scratchDir}
srun tar cf - . --use-compress-program="pigz" | rclone rcat ${acaciaAlias}:${acaciaOutPath} -q
EOF
)

# Only run the stage script if $acaciaInPath is set
stageJobID=
if [ -n "$acaciaInPath" ]
then
    stageJobID=$(printf '%s\n' "$stageScript" | sbatch --parsable)

    # Show the staging script
    echo
    echo "########## Begin stage script ##########"
    printf '%s\n' "$stageScript"
    echo "########## End stage script ##########"
fi

# Run the superScript if runSuper is set
# Depend on stageScript if stageJobID exists
superJobID=
if [ -n "$runSuper" ]
then
    if [ -n "$stageJobID" ]
    then
        superJobID=$(printf '%s\n' "$superScript" | sbatch --dependency=afterok:$stageJobID --parsable)
    else
        superJobID=$(printf '%s\n' "$superScript" | sbatch --parsable)
    fi

    # Print out the super script
    echo
    echo "########## Begin super script ##########"
    printf '%s\n' "$superScript"
    echo "########## End super script ##########"
fi


# Only run the store script if $acaciaOutPath is set
# Try to depend on superJobID, then fallback to stageJobID
storeJobID=
if [ -n "$acaciaOutPath" ]
then
    if [ -n "$superJobID" ]
    then
        storeJobID=$(printf '%s\n' "$storeScript" | sbatch --dependency=afterok:$superJobID --parsable)
    elif [ -n "$stageJobID" ]
    then
        storeJobID=$(printf '%s\n' "$storeScript" | sbatch --dependency=afterok:$stageJobID --parsable)
    else
        storeJobID=$(printf '%s\n' "$storeScript" | sbatch --parsable)
    fi

    # Show the storage script
    echo
    echo "########## Begin store script ##########"
    printf '%s\n' "$storeScript"
    echo "########## End store script ##########"
fi

squeue --me
