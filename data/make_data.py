#!/usr/bin/env python
import numpy as np
import os
import math
import zipfile
import datetime

# Bytes in a large file
large_file_size = 1000000

# Bytes in a log file
log_file_size = 100000

# Number of large files
nfiles = 100

# Number of log files
nlogs = 100

# Zip file name
zip_file = "data.zip"

# Name for the data directory
data_dir = "simulation"
bin_dir = "results"
log_dir = "log"

# Number of zeros to zfill
nzeros_bin=math.ceil(math.log10(nfiles))
nzeros_log=math.ceil(math.log10(nlogs))

# String pattern to repeat for log files
pattern = "The quick brown fox jumps over the log.\n"

# Fill the binary files with zeros and write to disk
array = np.zeros(large_file_size, dtype=np.uint8).tobytes()

# Make the log_string to write as a log file
ntimes = log_file_size // len(pattern) + 1
log_string = ((ntimes*pattern)[:log_file_size]).encode('ascii')

# Zip information for file creation date
now = datetime.datetime.now()

# Make the directories and data structure
with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as output_zip:
    for dname in [bin_dir, log_dir]:
        output_dir = f"{data_dir}/{dname}"
        #output_dir=os.path.join(data_dir, dname)
        if dname == bin_dir:
            for n in range(0, nfiles):
                # Numerical extension
                n_ext = str(n).zfill(nzeros_bin)
                filename = f"{output_dir}/data_{n_ext}.dat"       
                zinfo=zipfile.ZipInfo(filename=filename, date_time=(now.year, now.month, now.day, now.hour, now.minute, now.second))
                output_zip.writestr(zinfo, array, compress_type=zipfile.ZIP_DEFLATED)
            
        if dname == log_dir:
            for n in range(0, nlogs):
                # Numerical extension
                n_ext = str(n).zfill(nzeros_log)
                filename = f"{output_dir}/data_{n_ext}.log"
                zinfo=zipfile.ZipInfo(filename=filename, date_time=(now.year, now.month, now.day, now.hour, now.minute, now.second))
                output_zip.writestr(zinfo, log_string, compress_type=zipfile.ZIP_DEFLATED)

    output_zip.testzip()