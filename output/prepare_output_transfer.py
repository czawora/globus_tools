
import os
import datetime
import argparse
import glob
import pandas as pd

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

output_batch_file = "output_batch.txt"
output_bash_file = "output_transfer.sh"
output_batch_archive = "_output_script_archive"

print("*** you SHOULD be running this on biowulf")
print("*** make sure globus-cli is installed and findable in PATH -- https://docs.globus.org/cli/")
print("*** use 'globus whoami' to check your current globus login identity | use 'globus login' to login")

# arg parse
parser = argparse.ArgumentParser(description='')

parser.add_argument('--skip_sorts', action='store_true')
parser.add_argument('--skip_lfps', action='store_true')
parser.add_argument('--dest_72', action='store_true')
parser.add_argument('--dest_56', action='store_true')
parser.add_argument('--dest_CZ', action='store_true')
parser.add_argument('--transfer_dirs', nargs="+")
parser.add_argument('--sources', nargs="+")

args = parser.parse_args()

dest_72 = args.dest_72
dest_56 = args.dest_56
dest_CZ = args.dest_CZ

skip_sorts = args.skip_sorts
skip_lfps = args.skip_lfps
transfer_dirs = args.transfer_dirs
srcs = args.sources

if transfer_dirs is None or srcs is None:

	print("at least one argument is required for --transfer_dirs and --sources")
	exit(1)


if len(transfer_dirs) != len(srcs):
	print("provide a transfer directory for every source given")
	exit(1)


if dest_56 is False and dest_72 is False and dest_CZ is False:

	print("specify a destination flag --dest_56, --dest_72, --dest_CZ")
	exit(1)

elif dest_56 is True and dest_72 is False and dest_CZ is False:

	dest = "FRNU56"

elif dest_56 is False and dest_72 is True and dest_CZ is False:

	dest = "FRNU72"

elif dest_56 is False and dest_72 is False and dest_CZ is True:

	dest = "CZ"

else:

	print("you cannot use multiple destination flags")
	exit(1)


########################################################################################################
########################################################################################################
# make sure environment varibales are in place

globus_ID = pd.read_csv("../globus_ID.csv", header=None)

comment_rows_bin = globus_ID.isnull().any(axis=1).tolist()
not_comment_rows_bin = [not x for x in comment_rows_bin]

# remove comment lines
globus_ID = globus_ID[not_comment_rows_bin]

# get the NIH globus ID
NIH_GLOBUS_ID = globus_ID[globus_ID.iloc[:, 0].str.contains("NIH")][1].tolist()[0]
dest_GLOBUS_ID = globus_ID[globus_ID.iloc[:, 0].str.contains(dest)][1].tolist()[0]

print("\n\n")

print("dest detected as : " + dest)
print("dest_GLOBUS_ID = " + dest_GLOBUS_ID)

print("\n\n")

########################################################################################################
########################################################################################################


run_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# "subj" level folders, will look in each for session folders
for src in srcs:
	print("source = " + src)

# archive existing batch file
if os.path.isfile(output_batch_file):

	existing_batch = open(output_batch_file)

	# skip the # comment char
	existing_timestamp = existing_batch.readline()[1:].strip("\n")

	if os.path.isdir(output_batch_archive) is False:
		os.mkdir(output_batch_archive)

	os.rename(output_batch_file, output_batch_archive + "/" + existing_timestamp + "_batch.txt")

	existing_batch.close()

	os.rename(output_bash_file, output_batch_archive + "/" + existing_timestamp + "_transfer.sh")


# create new bash
new_bash = open(output_bash_file, 'w')
new_bash.write("#!/usr/bin/bash\n")

# create new batch
new_batch = open(output_batch_file, 'w')

# write timestamp
new_batch.write("#" + run_timestamp + "\n\n")

transfer_count = 0

# add transfers
for idx, src in enumerate(srcs):

	current_transfer_dir = transfer_dirs[idx]

	print("scanning source: " + src)
	print("planning to transfer to: " + current_transfer_dir)

	# note the src
	new_batch.write("#src = " + src + "\n")

	src_splits = src.split("/")

	if src_splits[-1] == "":
		src_name = src_splits[-2]
	else:
		src_name = src_splits[-1]

	if skip_sorts is False:

		src_glob = glob.glob(src + "/*/spike/outputs") + glob.glob(src + "/*/spike/_ignore_me.txt")

		sort_src_sessions = list(set( [ f.split("/spike")[0] for f in src_glob ] ))

		for sess in sort_src_sessions:

			print(sess)

			dest_sess_level = current_transfer_dir + "/" + sess.split("/")[-1]

			# check for ignore_mes
			for f in glob.glob(sess + "/spike/_ignore_me.txt"):

				fname = f.split("/")[-1]

				new_batch.write(sess + "/spike/" + fname)
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/" + fname)
				new_batch.write("\n")
				transfer_count += 1

			for f in glob.glob(sess + "/spike/outputs/*sortSummary.csv") + glob.glob(sess + "/spike/outputs/*spikeWaveform.mat") + glob.glob(sess + "/spike/outputs/*sortFigs"):

				fname = f.split("/")[-1]

				if os.path.isdir(f):
					new_batch.write(" --recursive ")

				new_batch.write(sess + "/spike/outputs/" + fname)
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/sorting/" + fname)
				new_batch.write("\n")
				transfer_count += 1

			for f in glob.glob(sess + "/spike/outputs/*spikeInfo.mat"):

				fname = f.split("/")[-1]

				if os.path.isdir(f):
					new_batch.write(" --recursive ")

				new_batch.write(sess + "/spike/outputs/" + fname)
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/raw/" + fname)
				new_batch.write("\n")
				transfer_count += 1

	if skip_lfps is False:

		# look for lfp results
		src_glob = glob.glob(src + "/*/lfp/outputs") + glob.glob(src + "/*/lfp/_ignore_me.txt")

		lfp_src_sessions = list(set( [ f.split("/lfp")[0] for f in src_glob ] ))

		for sess in lfp_src_sessions:

			print(sess)

			dest_sess_level = current_transfer_dir + "/" + sess.split("/")[-1]

			stimArtifactInfo_glob = glob.glob(sess + "/stimArtifactInfo.mat")
			if stimArtifactInfo_glob != []:
				new_batch.write(sess + "/stimArtifactInfo.mat")
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/stim/stimArtifactInfo.mat")
				new_batch.write("\n")

			# check for ignore_mes
			for f in glob.glob(sess + "/lfp/_ignore_me.txt"):

				fname = f.split("/")[-1]

				new_batch.write(sess + "/lfp/" + fname)
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/" + fname)
				new_batch.write("\n")
				transfer_count += 1

			for f in glob.glob(sess + "/lfp/outputs/microDev*") + glob.glob(sess + "/lfp/outputs/variance.csv"):

				print(f)
				fname = f.split("/")[-1]

				if os.path.isdir(f):
					new_batch.write(" --recursive ")

				new_batch.write(sess + "/lfp/outputs/" + fname)
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/cleaning/" + fname)
				new_batch.write("\n")
				transfer_count += 1

			for f in glob.glob(sess + "/lfp/outputs/*processed.mat") + glob.glob(sess + "/lfp/outputs/*noreref.mat"):

				fname = f.split("/")[-1]

				if os.path.isdir(f):
					new_batch.write(" --recursive ")

				new_batch.write(sess + "/lfp/outputs/" + fname)
				new_batch.write(" ")
				new_batch.write(dest_sess_level + "/raw/" + fname)
				new_batch.write("\n")
				transfer_count += 1


# now write the tranfer bash command
new_bash.write("globus transfer ")
new_bash.write(NIH_GLOBUS_ID)
new_bash.write(" ")
new_bash.write(dest_GLOBUS_ID)
new_bash.write(" --no-verify-checksum ")
new_bash.write(" --batch --label \"")
new_bash.write(run_timestamp + " transfer-" + str(transfer_count))
new_bash.write("\" < " + output_batch_file)

new_bash.close()
new_batch.close()
