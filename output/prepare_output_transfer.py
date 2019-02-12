
import os
import datetime
import argparse
import glob

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

output_batch_file = "output_batch.txt"
output_bash_file = "output_transfer.sh"
output_batch_archive = "_output_script_archive"

print("*** you SHOULD be running this on biowulf")
print("*** make sure globus-cli is installed and findable in PATH -- https://docs.globus.org/cli/")
print("*** use 'globus whoami' to check your current globus login identity | use 'globus login' to login")


########################################################################################################
########################################################################################################
# make sure environment varibales are in place

globus_ID = open("../globus_ID.csv")
globus_ID_lines = [l.strip("\n") for l in globus_ID]
globus_ID.close()

FRNU_GLOBUS_ID = globus_ID_lines[1].split(",")[-1]
NIH_GLOBUS_ID = globus_ID_lines[2].split(",")[-1]

os.environ["FRNU_GLOBUS"] = FRNU_GLOBUS_ID
os.environ["NIH_GLOBUS"] = NIH_GLOBUS_ID

print("\n\n")

print("env FRNU_GLOBUS = " + FRNU_GLOBUS_ID)
print("set FRNU_GLOBUS environment variable to FRNU's Globus endpoint ID specified in ../globus_ID.csv")

print("env NIH_GLOBUS = " + NIH_GLOBUS_ID)
print("set NIH_GLOBUS environment variable to NIH's Globus endpoint ID specified in ../globus_ID.csv")

print("\n\n")


########################################################################################################
########################################################################################################


# arg parse
parser = argparse.ArgumentParser(description='')

parser.add_argument('--transfer_dirs', nargs="+")
parser.add_argument('--sources', nargs="+")

args = parser.parse_args()

transfer_dirs = args.transfer_dirs
srcs = args.sources

if transfer_dirs is None or srcs is None:

    print("at least one argument is required for --transfer_dirs and --sources")
    exit(1)


if len(transfer_dirs) != len(srcs):
    print("provide a transfer directory for every source given")
    exit(1)


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

        for f in glob.glob(sess + "/lfp/outputs/refset*") + glob.glob(sess + "/lfp/outputs/variance.csv"):

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
new_bash.write(os.environ["NIH_GLOBUS"])
new_bash.write(" ")
new_bash.write(os.environ["FRNU_GLOBUS"])
new_bash.write(" --no-verify-checksum ")
new_bash.write(" --batch --label \"")
new_bash.write(run_timestamp + " transfer-" + str(transfer_count))
new_bash.write("\" < " + output_batch_file)

new_bash.close()
new_batch.close()
