#!/usr/bin/env python3

from datetime import datetime
import subprocess
import os
import string

# The project you want to charge to
account=os.environ['PAWSEY_PROJECT']

# ID for this run, use local time zone for now
dateTime=datetime.now().strftime("%Y%m%d-LOCAL-%H-%M-%S")

# Your alias for interacting with Acacia
acaciaAlias="acacia-mine"

# Your chosen bucket name (must edit this)
BucketName="courses01-acacia-tmp"

# Set copy_queue and debug_queue and rclone version
copy_queue="copy"
debug_queue="debug"
rclone_version="1.63.1"

# Path to get files from Acacia, set this to None for no staging
acaciaInPath=f"{BucketName}/simulation.tar.gz"

# Path to put files on Acacia, set this to None for no storing
acaciaOutPath=f"{BucketName}/simulation-{dateTime}.tar.gz"

# Path in scratch to work from
scratchDir=f"/scratch/{account}/{os.environ['USER']}/work"

# actually Run the super job?
runSuper=True

# Store the stage-in script in a variable called stageScript
# anything in curly brackets in the string {} is replaced
# with the python variable of the same name

# Use backslash (\) to escape anything that Python considers a special character
# into the script (e.g \\ or \n), dollar signs are not special
# First line of script must start with #!/bin/bash (no whitespace prior to!)

stageScript=f"""#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --job-name=stageTar
#SBATCH --partition={copy_queue}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=00:05:00

module load rclone/{rclone_version}

# Stage files from Acacia

# Streaming approach
srun mkdir -p {scratchDir}
srun rclone cat {acaciaAlias}:{acaciaInPath} -q | tar xf - --directory {scratchDir}/ --use-compress-program="pigz"
"""

# Store the job script in a variable called superScript
# edit this for your own use
superScript=f"""#!/bin/bash --login
#SBATCH --account={account}
#SBATCH --partition={debug_queue}
#SBATCH --job-name=superJob
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:01:00

module load rclone/1.58.1

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
#SBATCH --partition={copy_queue}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=00:05:00

module load rclone/{rclone_version}

# Store files to Acacia

# Streaming approach
# Use zcf or jcf for a compressed archive
cd {scratchDir}
srun tar cf - . --use-compress-program="pigz" | rclone rcat {acaciaAlias}:{acaciaOutPath} -q
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
    stageJobID=run_cmds("sbatch --parsable", std_input=stageScript).split()[0].strip()

    # Print out the stage script
    print(f"########## Begin stage script ##########")
    print(stageScript)
    print(f"########## End stage script ##########")

# Actually run the super job?
superJobID=None
if runSuper:
    if stageJobID is None:
        # No dependency on stage script
        cmds="sbatch --parsable"
    else:
        # Dependency on stage script
        cmds=f"sbatch --dependency=afterok:{stageJobID} --parsable"
    
    # Run the super script and extract JobID
    superJobID=run_cmds(cmds, std_input=superScript).split()[0].strip()

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
        cmds=f"sbatch --dependency=afterok:{superJobID} --parsable"
    elif stageJobID is not None:
        # Depend on the stage job
        cmds=f"sbatch --dependency=afterok:{stageJobID} --parsable"
    else:
        # No dependency
        cmds=f"sbatch --parsable"

    # Run the store script and extract JobID
    storeJobID=run_cmds(cmds, std_input=storeScript).split()[0].strip()

    # Print out the store script
    print(f"\n########## Begin store script ##########")
    print(storeScript)
    print(f"########## End store script ##########")

# Check to see if the commands have been submitted
print(run_cmds("squeue --me"))
