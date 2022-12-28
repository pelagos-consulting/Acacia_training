#!/usr/bin/env python3

from datetime import datetime
import subprocess
import os
import string

# The project you want to charge to
account="courses01"

# ID for this run, use local time zone for now
dateTime=datetime.now().strftime("%Y%m%d-LOCAL-%H-%M-%S")

# Your alias for interacting with Acacia
acaciaAlias="acacia-mine"

# Path to get files from Acacia, set this to None for no staging
acaciaInPath=f"{account}-acacia-2022/simulation.tar"

# Path to put files on Acacia, set this to None for no storing
acaciaOutPath=f"{account}-acacia-2022/simulation-{dateTime}.tar"

# Path in scratch to work from
scratchDir=f"/scratch/{account}/{os.environ['USER']}/working"

# actually Run the super job?
runSuper=True

# Store the stage-in script in a variable called stageScript
# edit these for your own use, 
# use curly brackets in the string {} 
# to put any python variables straight into the script
# Use the backslash (\) to insert special characters into the script 
# e.g \\ to insert a single backslash
# First line of script must start with #!/bin/bash (no whitespace prior to!)

stageScript=f"""#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --job-name=stageTar
#SBATCH --partition=copyq
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --export=NONE

module load miniocli rclone

# Stage files from Acacia

# Streaming approach
srun mkdir -p {scratchDir}
srun rclone cat {acaciaAlias}:{acaciaInPath} | tar xf - --directory {scratchDir}/ 

# Copy approach
#cd {scratchDir}
#srun mc cp --md5 --quiet {acaciaAlias}/{acaciaInPath} {scratchDir}/archive.tar > /dev/null
#srun tar xf archive.tar
#rm archive.tar
"""

# Store the job script in a variable called superScript
# edit this for your own use
superScript=f"""#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --partition=debugq
#SBATCH --job-name=superJob
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --export=NONE

module load miniocli rclone

srun mkdir -p {scratchDir}
cd {scratchDir}
hostname

# Make an empty file
touch run-{dateTime}.txt 

echo srun toolName arguments
"""

# Store the store script in a variable called storeScript
# edit this for your own use
storeScript=f"""#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --job-name=storeTar
#SBATCH --partition copyq
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --export=NONE

module load miniocli rclone

# Store files to Acacia

# Streaming approach
# Use zcf or jcf for a compressed archive
cd {scratchDir}
srun tar cf - . | rclone rcat {acaciaAlias}:{acaciaOutPath}

# Copy approach
#srun tar cf archive.tar .
#srun mc cp --md5 --quiet archive.tar {acaciaAlias}/{acaciaOutPath} > /dev/null
#rm archive.tar
"""

### Edit anything below this line at your own risk ###

def run_cmds(cmds, std_input=None):
    # This is just a way to run a list of commands (cmds)
    # and use some text (std_input) as standard input to the commands

    # Make sure arguments are correct
    assert(isinstance(cmds, str)), "Input commands must be a string"
    assert(isinstance(std_input, str) or std_input is None), "Input script must be a string or None"

    if std_input is not None:
        # Run cmds with std_input as standard input
        p=subprocess.run(cmds, 
            input=std_input, 
            shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
            encoding='ascii'
		)
    else:
        # Run cmds without standard input
        p=subprocess.run(cmds,  
            shell=True, 
            encoding='ascii',
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)

    # Check for errors
    if (p.returncode != 0):
        print(f"#### Std out:\n{p.stdout}")
        raise RuntimeError(f"#### Std err:\n{p.stderr}")

    # Return the text output from running the command
    return p.stdout

#### Main program ####

# Only run the stage script if the variable "acaciaInPath" is valid
stageJobID=None
if ((acaciaInPath is not None) and (acaciaInPath != "")):
    # Run the stage script and extract JobID
    stageJobID=run_cmds("sbatch", std_input=stageScript).split()[3].strip()

    # Print out the stage script
    print(f"########## Begin stage script ##########")
    print(stageScript)
    print(f"########## End stage script ##########")

# Actually run the super job?
superJobID=None
if runSuper:
    if stageJobID is None:
        # No dependency on stage script
        cmds="sbatch"
    else:
        # Dependency on stage script
        cmds=f"sbatch --dependency=afterok:{stageJobID}"
    
    # Run the super script and extract JobID
    superJobID=run_cmds(cmds, std_input=superScript).split()[3].strip()

    # Print out the super script
    print(f"\n########## Begin super script ##########")
    print(superScript)
    print(f"########## End super script ##########")

# Only run the store job if the variable "acaciaOutPath" is valid
# Is dependent on stage script if super script is not run
storeJobID=None
if ((acaciaOutPath is not None) and (acaciaOutPath != "")):
    # Run the storeScript and
    # get field 4 from the output 
    if superJobID is not None:
        # Depend on the super job
        cmds=f"sbatch --dependency=afterok:{superJobID}"
    elif stageJobID is not None:
        # Depend on the stage job
        cmds=f"sbatch --dependency=afterok:{stageJobID}"
    else:
        # No dependency
        cmds=f"sbatch"

    # Run the store script and extract JobID
    storeJobID=run_cmds(cmds, std_input=storeScript).split()[3].strip()

    # Print out the store script
    print(f"\n########## Begin store script ##########")
    print(storeScript)
    print(f"########## End store script ##########")

# Check to see if the commands have been submitted
print(run_cmds("squeue --me"))
