#!/usr/bin/python3

import os
import datetime
import argparse
import re
import csv
import pandas as pd


def takeDate(elem):
	return(elem["date_YMD_HM"])


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

input_batch_file = "input_batch.txt"
input_bash_file = "input_transfer.sh"
input_batch_archive = "_input_script_archive"

sess_info_temp_dir = "/Volumes/56A/UTAH_A/globus/temp"
if os.path.isdir(sess_info_temp_dir) is False:
	os.mkdir(sess_info_temp_dir)

########################################################################################################
########################################################################################################
# make sure environment varibales are in place

globus_ID = open("../globus_ID.csv")
globus_ID_lines = [l.strip("\n") for l in globus_ID]
globus_ID.close()

FRNU_GLOBUS_ID = globus_ID_lines[0].split(",")[-1]
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

parser = argparse.ArgumentParser(description='build list of dir + files to transfer to biowulf, also write transfer script')

parser.add_argument('subj_path')
parser.add_argument('biowulf_dest_path')
parser.add_argument('nsp_suffix')
parser.add_argument('--raw_dir', default='data_raw')
parser.add_argument('--sesslist', default='')

parser.add_argument('--dry_run', action='store_true')

parser.add_argument('--skip_backup_analog', action='store_false')
parser.add_argument('--skip_backup_digital', action='store_false')

args = parser.parse_args()

subj_path = args.subj_path
biowulf_dest_path = args.biowulf_dest_path
nsp_suffix = args.nsp_suffix
raw_dir = args.raw_dir
sesslist = args.sesslist

use_backup_analog = args.skip_backup_analog
use_backup_digital = args.skip_backup_digital

dry_run = args.dry_run

session_path = subj_path + "/" + raw_dir

subj = subj_path.split("/")[-1]


########################################################################################################
########################################################################################################
# make sure paths from arguments exist

if sesslist != "" and os.path.isfile(sesslist) is False:
	print("value passed as --sesslist is not a valid path")
	exit(-1)

if os.path.isdir(subj_path) is False:
	print("value passed as --subj_path is not a valid path")
	exit(-1)

datestring_regex = re.compile(r'(\d\d\d\d\d\d_\d\d\d\d).*')

recording_filesets = []

if sesslist == "":

	session_path_ls = os.listdir(session_path)

else:

	session_path_ls = []

	sesslist_f = open(sesslist)
	sesslist_csv = csv.reader(sesslist_f, delimiter=",")

	session_path_ls = [l[1] for l in sesslist_csv]

	sesslist_f.close()

id_counter = 1

for sess in session_path_ls:

	# check for good session name
	sessname_match = re.match(datestring_regex, sess)

	if sessname_match is not None:

		datestring_match = re.findall(datestring_regex, sess)[0]

		sess_path = subj_path + "/" + sess

		# load the jacksheet
		jacksheet_fpath = sess_path + "/jacksheetBR_complete.csv"
		jacksheet_data = pd.read_csv(jacksheet_fpath)

		jacksheet_data_nsp = jacksheet_data.loc[jacksheet_data["NSPsuffix"] == nsp_suffix]
		jacksheet_data_nsp_micro = jacksheet_data.loc[jacksheet_data["MicroDevNum"] >= 1]

		jacksheet_data_other_nsp = jacksheet_data.loc[jacksheet_data["NSPsuffix"] != nsp_suffix]

		# check that there are micro channels with this NSPsuffix
		if jacksheet_data_nsp_micro.shape[0] != 0:

			# are all the remaining channels from the same nsx file
			jacksheet_data_nsp_micro_fnames = jacksheet_data_nsp_micro.FileName.unique()

			if jacksheet_data_nsp_micro_fnames.shape[0] > 1:

				print("micro channels on chosen nsp are split across multiple nsx files, should not happen!")
				exit(1)

			# found an nsx file to transfer
			current_nsx_file = jacksheet_data_nsp_micro_fnames[0]
			current_nsx_fileExt = current_nsx_file[-3:]

			# find an nev and ns3 file in this nsp
			current_analog_pulse_file = ""
			current_analog_pulse_fileExt = ""
			current_analog_pulse_nsp = ""

			current_digital_pulse_file = ""
			current_digital_pulse_nsp = ""

			# first analog pulses: find non-ns5/6 files that contain an ain channel
			jacksheet_data_nsp_ain = jacksheet_data_nsp[jacksheet_data_nsp["ChanName"].str.contains("ain") & jacksheet_data_nsp["FileName"].str.contains("ns") & (jacksheet_data_nsp["SampFreq"] < 3e4)]

			# any results?
			if jacksheet_data_nsp_ain.shape[0] != 0:

				# are these channels present on more than one of: ns2, ns3, or ns4?
				if jacksheet_data_nsp_ain.shape[0] != 1:
					print("analog ain channels are spread on multiple nsx files in this NSP")
					exit(2)

				current_analog_pulse_file = jacksheet_data_nsp_ain.FileName.tolist()[0]
				current_analog_pulse_nsp = jacksheet_data_nsp_ain.NSPsuffix.tolist()[0]
				current_analog_pulse_fileExt = current_analog_pulse_file[-3:]

			# found no files, if allowed used the ain's from the other NSP
			else:

				if use_backup_analog is True:

					# find non-ns5/6 files that contain an ain channel
					jacksheet_data_other_nsp_ain = jacksheet_data_other_nsp[jacksheet_data_other_nsp["ChanName"].str.contains("ain") & jacksheet_data_other_nsp["FileName"].str.contains("ns") & (jacksheet_data_other_nsp["SampFreq"] < 3e4)]

					# any results?
					if jacksheet_data_other_nsp_ain.shape[0] != 0:

						# are these channels present on more than one of: ns2, ns3, or ns4?
						if jacksheet_data_other_nsp_ain.shape[0] != 1:
							print("analog ain channels on backup NSP are spread on multiple nsx files")
							exit(2)

						print("****** using analog pulse file from other NSP *******")
						current_analog_pulse_file = jacksheet_data_other_nsp_ain.FileName.tolist()[0]
						current_analog_pulse_nsp = jacksheet_data_other_nsp_ain.NSPsuffix.tolist()[0]
						current_analog_pulse_fileExt = current_analog_pulse_file[-3:]

					else:
						print("****** for session: " + sess + ", no analog pulses on either NSP *******")

			# now look for nev files
			jacksheet_data_nsp_din = jacksheet_data_nsp[jacksheet_data_nsp["ChanName"].str.contains("ain") & jacksheet_data_nsp["FileName"].str.contains("nev")]

			# any results?
			if jacksheet_data_nsp_din.shape[0] != 0:

				current_digital_pulse_file = jacksheet_data_nsp_din.FileName.tolist()[0]
				current_digital_pulse_nsp = jacksheet_data_nsp_din.NSPsuffix.tolist()[0]

			# check other nsp for nev file
			else:

				if use_backup_digital is True:

					jacksheet_data_other_nsp_din = jacksheet_data_other_nsp[jacksheet_data_other_nsp["ChanName"].str.contains("ain") & jacksheet_data_other_nsp["FileName"].str.contains("nev")]

					# any results?
					if jacksheet_data_other_nsp_din.shape[0] != 0:

						print("****** using digital pulse file from other NSP *******")
						current_digital_pulse_file = jacksheet_data_other_nsp_din.FileName.tolist()[0]
						current_digital_pulse_nsp = jacksheet_data_other_nsp_din.NSPsuffix.tolist()[0]

					else:
						print("****** for session: " + sess + ", no digital pulses on either NSP *******")

			session_fileset = {}

			session_fileset.update({"date_YMD_HM": datestring_match})

			session_fileset.update({"session_path": sess_path})
			session_fileset.update({"session_name": sess})

			session_info_str = current_nsx_fileExt + "\n" + current_analog_pulse_fileExt
			session_fileset.update({"session_info_str": session_info_str})
			session_fileset.update({"session_jacksheet": "jacksheetBR_complete.csv"})

			session_fileset.update({"analog_physio_src": current_nsx_file})
			session_fileset.update({"analog_physio_dest": subj + "_" + datestring_match + "_" + nsp_suffix + "." + current_nsx_fileExt})
			session_fileset.update({"analog_physio_filesize": os.path.getsize(sess_path + "/" + current_nsx_file)})

			if current_analog_pulse_file != "":

				session_fileset.update({"analog_pulse_src": current_analog_pulse_file})
				session_fileset.update({"analog_pulse_dest": subj + "_" + datestring_match + "_" + current_analog_pulse_nsp + "." + current_analog_pulse_fileExt})
				session_fileset.update({"analog_pulse_filesize": os.path.getsize(sess_path + "/" + current_analog_pulse_file)})

			else:

				session_fileset.update({"analog_pulse_src": ""})
				session_fileset.update({"analog_pulse_dest": ""})
				session_fileset.update({"analog_pulse_filesize": 0})

			if current_digital_pulse_file != "":

				session_fileset.update({"digital_pulse_src": current_digital_pulse_file})
				session_fileset.update({"digital_pulse_dest": subj + "_" + datestring_match + "_" + current_digital_pulse_nsp + ".nev"})
				session_fileset.update({"digital_pulse_filesize": os.path.getsize(sess_path + "/" + current_digital_pulse_file)})

			else:

				session_fileset.update({"digital_pulse_src": ""})
				session_fileset.update({"digital_pulse_dest": ""})
				session_fileset.update({"digital_pulse_filesize": 0})

			session_fileset.update({"id": id_counter})
			session_fileset.update({"session_concat_string": session_fileset["analog_physio_src"] + session_fileset["digital_pulse_src"] + session_fileset["analog_pulse_src"]})
			session_fileset.update({"session_filesize": session_fileset["analog_physio_filesize"]})

			recording_filesets.append(session_fileset)


# sort the filesets
recording_filesets = sorted(recording_filesets, key=takeDate)

# seperate the empty ones
empty_filesets = [s for s in recording_filesets if s["session_filesize"] == 0]

# from the non-empty ones
input_filesets = [s for s in recording_filesets if s["session_filesize"] != 0]
input_session_size = sum([s["session_filesize"] for s in input_filesets])
input_session_names = [s["session_name"] for s in input_filesets]

print("num filesets: " + str(len(input_filesets)))

# remove filesets that include all the same files, might not be necessary after switch to jacksheet
for rec_set1 in input_filesets:
	for rec_set2 in input_filesets:

		if rec_set1["id"] != rec_set2["id"]:
			if rec_set1["session_concat_string"] == rec_set2["session_concat_string"]:

				print(rec_set1["session_name"] + " is duplicated!")

				input_filesets.remove(rec_set2)

print("num filesets after duplicate removal: " + str(len(input_filesets)))
print("\n\n")

########################################################################################################
########################################################################################################
# dry run stats

if dry_run:

	print("found the following files in " + subj_path)

	for sess in input_filesets:
		print(sess["session_name"] + " ( " + str(sess["session_filesize"]/1e9) + " Gb )")

	print()
	print("excluded empty sessions (" + str(len(empty_filesets)) + ") : ")

	for sess in empty_filesets:
		print(sess["session_name"] + " ( " + str(sess["session_filesize"]/1e9) + " Gb )")

	print(str(len(input_filesets)) + " sessions ( " + str(input_session_size/1e9) + " Gb / " + str(input_session_size/1e12) + " Tb ) will be uploaded")

	exit(0)

########################################################################################################
########################################################################################################
# make list of files that will be transferred within memory limit

current_upload_list = input_filesets
mem_count = input_session_size/1e9

print(str(len(current_upload_list)) + " sessions ( " + str(mem_count) + " Gb ) to be uploaded")

########################################################################################################
########################################################################################################
# archive old transfer scripts

run_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

if os.path.isfile(input_batch_file):

	existing_batch = open(input_batch_file)

	# skip the # comment char
	existing_timestamp = existing_batch.readline()[1:].strip("\n")

	if os.path.isdir(input_batch_archive) is False:
		os.mkdir(input_batch_archive)

	os.rename(input_batch_file, input_batch_archive + "/" + existing_timestamp + "_batch.txt")

	existing_batch.close()

	os.rename(input_bash_file, input_batch_archive + "/" + existing_timestamp + "_transfer.sh")


########################################################################################################
########################################################################################################
# prepare transfer scripts

transfer_count = len(current_upload_list)

new_bash = open(input_bash_file, 'w')

new_bash.write("#!/usr/bin/bash\n\n")

# now write the transfer bash command
new_bash.write("globus transfer ")
new_bash.write(os.environ["FRNU_GLOBUS"])
new_bash.write(" ")
new_bash.write(os.environ["NIH_GLOBUS"])
new_bash.write(" --no-verify-checksum ")
new_bash.write(" --sync-level size ")
new_bash.write(" --batch --label \"")
new_bash.write(run_timestamp + " transfer-" + str(transfer_count) + "sess")
new_bash.write("\" < " + input_batch_file.split("/")[-1])

new_bash.close()

new_batch = open(input_batch_file, 'w')

# write timestamp
new_batch.write("#" + run_timestamp + "\n")
new_batch.write("#subj_path: " + subj_path + "\n")
new_batch.write("#nsp_suffix: " + nsp_suffix + "\n")
new_batch.write("#raw_dir: " + raw_dir + "\n")
new_batch.write("#transfer sess count: " + str(transfer_count) + "\n")
new_batch.write("\n\n")

for sess in current_upload_list:

	new_batch.write(sess["session_path"] + "/" + sess["analog_physio_src"])
	new_batch.write(" ")
	new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + sess["analog_physio_dest"])
	new_batch.write("\n")

	if sess["analog_pulse_src"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["analog_pulse_src"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + sess["analog_pulse_dest"])
		new_batch.write("\n")

	if sess["digital_pulse_src"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["digital_pulse_src"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + sess["digital_pulse_dest"])
		new_batch.write("\n")

	sess_info_file = open(sess_info_temp_dir + "/" + subj + "_" + sess["session_name"] + "_info.txt", 'w')
	sess_info_file.write(sess["session_info_str"])
	sess_info_file.close()

	new_batch.write(sess_info_temp_dir + "/" + subj + "_" + sess["session_name"] + "_info.txt")
	new_batch.write(" ")
	new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + "_info.txt")
	new_batch.write("\n")

new_batch.close()


print("\n\n")
print("biowulf_dest_path: " + biowulf_dest_path)
print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  -- MAKE SURE THIS IS RIGHT\n\n")
print('\n\n')

print("next run 'bash input_transfer.sh' (or look inside input_batch.txt to make sure you included all the files you wanted)")
