 

import sys
import os
import subprocess
import datetime
import argparse
import glob

#important paths
nih_dest = "/data/zaworaca/data"
batch_file = "/Users/zaworaca/dev/biowulf_weeds/globus/input/input_batch.txt"
bash_file = "/Users/zaworaca/dev/biowulf_weeds/globus/input/input_transfer.sh"
batch_archive = "/Users/zaworaca/dev/biowulf_weeds/globus/input/_input_script_archive"


########################################################################################################
########################################################################################################
#make sure environment varibales are in place

try:
	checker = os.environ["MAC_GLOBUS"]

except:
	print("set MAC_GLOBUS environment variable to your local computer's Globus endpoint ID")
	exit(-2)

try:
	checker = os.environ["NIH_GLOBUS"]

except:
	print("set NIH_GLOBUS environment variable to the NIH Globus endpoint ID")
	exit(-3)

########################################################################################################
########################################################################################################
#make sure globus connection works

print(["globus", "ls", os.environ["NIH_GLOBUS"] + ":~"])

globus_login_check = str(subprocess.check_output(["globus", "ls", os.environ["NIH_GLOBUS"] + ":/~"]))

if "Globus CLI Error" in globus_login_check:
	print("globus login check: FAIL, need to 'globus login' first")
	exit(1)
else:
	print("globus login check: GOOD")


########################################################################################################
########################################################################################################
#parse input arguments

parser = argparse.ArgumentParser(description = 'build list of dir + files to transfer to biowulf, also write transfer script')
parser.add_argument('--glob', required = True)
parser.add_argument('--subj', required = True)
parser.add_argument('--mem_limit_gb', required = True)
parser.add_argument('--ref_list', required = True)
args = parser.parse_args()

glob_pat = args.glob
subj = args.subj
mlimit = args.mem_limit_gb
ref_list = args.ref_list

subj_root_nih = nih_dest + "/" + subj


########################################################################################################
########################################################################################################

run_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

#archive existing batch file
if os.path.isfile(batch_file):

	existing_batch = open(batch_file)
	
	#skip the # comment char
	existing_timestamp = existing_batch.readline()[1:].strip("\n")

	if os.path.isdir(batch_archive) == False:
		os.mkdir(batch_archive)

	os.rename(batch_file, batch_archive + "/" + existing_timestamp + "_batch.txt")

	existing_batch.close()

	os.rename(bash_file, batch_archive + "/" + existing_timestamp + "_transfer.sh")


matching_files = glob.glob(glob_pat)
matching_file_sizes = [os.path.getsize(i) for i in matching_files]

transfer_count = len(matching_files)

print("transferring " + str(transfer_count) + " files, totaling " + str(sum(matching_file_sizes)/1e9) + " Gb " + "( " + str(sum(matching_file_sizes)/1e12) + " Tb )")

matching_file_dirs_tmp = [i.split("/")[-1] for i in matching_files]
matching_file_dirs = [i.split(".")[0] for i in matching_file_dirs_tmp]

matching_dirs_nih = [subj_root_nih + "/" + i for i in matching_file_dirs]
matching_files_nih = []

for iFile in range(transfer_count):
	matching_files_nih.append(subj_root_nih + "/" + matching_file_dirs[iFile] + "/" + matching_file_dirs_tmp[iFile])

########################################################################################################
########################################################################################################
#create new bash 

new_bash = open(bash_file, 'w')
new_bash.write("#!/usr/bin/bash\n\n")

new_bash.write("globus mkdir " + os.environ["NIH_GLOBUS"] + ":" + subj_root_nih + "\n")

for d in matching_dirs_nih:
	new_bash.write("globus mkdir " + os.environ["NIH_GLOBUS"] + ":" + d + "\n")

#now write the transfer bash command
new_bash.write("globus transfer ")
new_bash.write(os.environ["MAC_GLOBUS"])
new_bash.write(" ") 
new_bash.write(os.environ["NIH_GLOBUS"])
new_bash.write(" --batch --label \"")
new_bash.write(run_timestamp + " transfer-" + str(transfer_count))
new_bash.write("\" < " + batch_file)

new_bash.close()

########################################################################################################
########################################################################################################
#create new batch

new_batch = open(batch_file, 'w')

#write timestamp
new_batch.write("#" + run_timestamp + "\n")
new_batch.write("#" + "pattern: " + glob_pat)
new_batch.write("\n\n")

for iFile in range(transfer_count):
	new_batch.write(matching_files[iFile] + " " + matching_files_nih[iFile] + "\n") 

new_batch.close()



