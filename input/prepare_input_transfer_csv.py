import os
import csv
import re
import glob
import argparse
import datetime


def takeDate(elem):
	return((elem["date_YMD"], elem["date_HM"]))


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
#  make sure environment varibales are in place

globus_ID = open("../globus_ID.csv")
globus_ID_lines = [l.strip("\n") for l in globus_ID]
globus_ID.close()

FRNU_GLOBUS_ID = globus_ID_lines[0].split(",")[-1]
NIH_GLOBUS_ID = globus_ID_lines[2].split(",")[-1]

os.environ["FRNU_GLOBUS"] = FRNU_GLOBUS_ID
os.environ["NIH_GLOBUS"] = NIH_GLOBUS_ID

print("env FRNU_GLOBUS = " + FRNU_GLOBUS_ID)
print("set FRNU_GLOBUS environment variable to FRNU's Globus endpoint ID specified in ../globus_ID.csv")

print("env NIH_GLOBUS = " + NIH_GLOBUS_ID)
print("set NIH_GLOBUS environment variable to NIH's Globus endpoint ID specified in ../globus_ID.csv")

print("\n\n")

########################################################################################################
########################################################################################################
# load implant region codes

implant_region_code_lines = []

implant_region_codes_f = open("../implant_region_codes.csv")
implant_region_codes_csv = csv.reader(implant_region_codes_f, delimiter=",")

implant_region_code_lines = [l for l in implant_region_codes_csv]

implant_region_codes_f.close()

implant_region_names = [l[0].strip(" ") for l in implant_region_code_lines]
implant_region_numcode = [l[1].strip(" ") for l in implant_region_code_lines]


########################################################################################################
########################################################################################################
# load micro reference sets

micro_reference_sets_lines = []

micro_reference_sets_f = open("../micro_reference_sets.csv")
micro_reference_sets_csv = csv.reader(micro_reference_sets_f, delimiter=",")

micro_reference_sets_lines = [l for l in micro_reference_sets_csv]

micro_reference_sets_f.close()

micro_reference_set_name = [l[0].strip(" ") for l in micro_reference_sets_lines]
micro_reference_subj = [l[1].strip(" ") for l in micro_reference_sets_lines]
micro_reference_channel_string = [l[2].strip(" ") for l in micro_reference_sets_lines]
micro_reference_channel_num_set = [l[3].strip(" ") for l in micro_reference_sets_lines]
micro_reference_array_num = [l[4].strip(" ") for l in micro_reference_sets_lines]
micro_reference_array_location = [l[5].strip(" ") for l in micro_reference_sets_lines]
micro_reference_description = [l[6].strip(" ") for l in micro_reference_sets_lines]


########################################################################################################
########################################################################################################

parser = argparse.ArgumentParser(description='build list of dir + files to transfer to biowulf, also write transfer script')

parser.add_argument('biowulf_dest_path')
parser.add_argument('sesslist')
parser.add_argument('sessname')

parser.add_argument('--fname_regex_include', default = '.*')
parser.add_argument('--fname_regex_exclude', default = '#')

parser.add_argument('--reference_set', default = '')

parser.add_argument('--ns5', action='store_true')
parser.add_argument('--ns6', action='store_true')

parser.add_argument('--analog_pulse', default = 'ns3', nargs = '?', choices = ['ns2', 'ns3', 'ns4', 'ns5', 'ns6', 'None'], help = 'which file extension in the session folder contains the analog pulses, or None to ignore')

parser.add_argument('--dry_run', action='store_true')

args = parser.parse_args()

biowulf_dest_path = args.biowulf_dest_path
sesslist = args.sesslist
sessname = args.sessname

reference_set = args.reference_set

fname_regex_include = args.fname_regex_include
fname_regex_exclude = args.fname_regex_exclude

ns5 = args.ns5
ns6 = args.ns6

analog_pulse = args.analog_pulse

dry_run = args.dry_run

datestring_regex = re.compile(r'.*(\d\d\d\d\d\d_\d\d\d\d).*')
subjstring_regex = re.compile(r'.*(NIH\d\d\d).*')

digital_pulse = "nev"
use_backup_analog = True
use_backup_digital = True

if os.path.isfile(sesslist) is False:
	print(sesslist + " is not a valid filepath.")
	exit(-1)

if ns5 and ns6:
	print("only choose either ns5 or ns6, there should be no reason to need both")
	exit(2)


include_re_pattern = re.compile(fname_regex_include)
exclude_re_pattern = re.compile(fname_regex_exclude)

if reference_set is "" or reference_set not in micro_reference_set_name:
	print("reference_set must be a string present in the first column of this table")

	for el, idx in enumerate(micro_reference_set_name):
		print("\t".join([micro_reference_set_name[idx], micro_reference_subj[idx], micro_reference_channel_string[idx], micro_reference_channel_num_set[idx], micro_reference_array_num[idx], micro_reference_array_location[idx], micro_reference_description[idx]]))

	print()
	exit(1)

else:
	reference_set_index = micro_reference_set_name.index(reference_set)
	implant_region_index = implant_region_names.index(micro_reference_array_location[reference_set_index])
	current_implant_region_numcode = implant_region_numcode[implant_region_index]


# read the csv
sesslist_csv_rows = []

sesslist_f = open(sesslist)
sesslist_csv = csv.reader(sesslist_f, delimiter=",")

sesslist_csv_rows = [l for l in sesslist_csv]

sesslist_f.close()


# read the rows of the csv file
recording_filesets = []

for csv_row in sesslist_csv_rows:

	current_sess_path = csv_row[0].strip(" ")
	current_sess_name = csv_row[1].strip("\n").strip(" ")

	current_sess_inclusion_str = csv_row[1].strip(" ")
	current_sess_exclusion_str = csv_row[2].strip(" ")
	current_sess_analog_ext = analog_pulse
	current_sess_physio_ext = physio_ext

	session_info_str = "\n".join([current_sess_analog_ext, current_sess_physio_ext])

	# check for good session name
	sessname_match = re.match(datestring_regex, current_sess_path)

	if sessname_match is not None:

		datestring_match = re.findall(datestring_regex, current_sess_path)[0]
		datestring_YMD = datestring_match.split("_")[0]
		datestring_HM = datestring_match.split("_")[1]

		subjname = re.findall(subjstring_regex, current_sess_path)[0]

		session_fileset = {}

		session_fileset.update({"date_YMD": datestring_YMD})
		session_fileset.update({"date_HM": datestring_HM})

		session_fileset.update({"subj": subjname})
		session_fileset.update({"session_path": current_sess_path})
		session_fileset.update({"session_name": subjname + "_" + datestring_match + "_" + sessname})
		session_fileset.update({"session_info_str": session_info_str})

		session_fileset.update({"ns6": ""})
		session_fileset.update({"ns6_filesize": 0})

		session_fileset.update({"ns5": ""})
		session_fileset.update({"ns5_filesize": 0})

		session_fileset.update({"analog_pulse": ""})
		session_fileset.update({"analog_pulse_filesize": 0})

		session_fileset.update({"digital_pulse": ""})
		session_fileset.update({"digital_pulse_filesize": 0})

		# current_sess_path_filestub = current_sess_path + "/" + datestring_match + "_" + current_sess_nsp
		physio_glob = glob.glob(current_sess_path + "/*." + current_sess_physio_ext)
		analog_pulse_glob = glob.glob(current_sess_path + "/*." + current_sess_analog_ext)
		digital_pulse_glob = glob.glob(current_sess_path + "/*." + digital_pulse)

		if physio_glob != []:

			for found_file in physio_glob:

				if current_sess_inclusion_str in found_file:

					if current_sess_exclusion_str is "None" or (current_sess_exclusion_str is not "None" and current_sess_exclusion_str not in found_file):

						filesize = os.path.getsize(found_file)

						if current_sess_physio_ext == "ns5":

							session_fileset["ns5"] = found_file.split("/")[-1]
							session_fileset["ns5_filesize"] = filesize

						elif current_sess_physio_ext == "ns6":

							session_fileset["ns6"] = found_file.split("/")[-1]
							session_fileset["ns6_filesize"] = filesize

						else:
							print("physio_ext entered for session '" + current_sess_path + "' is neither ns5 nor ns6")

		if current_sess_analog_ext != "None" and analog_pulse_glob != []:

			for found_file in analog_pulse_glob:

				if current_sess_inclusion_str in found_file:
					if current_sess_exclusion_str is "None" or (current_sess_exclusion_str is not "None" and current_sess_exclusion_str not in found_file):

						filesize = os.path.getsize(found_file)
						session_fileset["analog_pulse"] = found_file.split("/")[-1]
						session_fileset["analog_pulse_filesize"] = filesize

			if session_fileset["analog_pulse"] == "" and use_backup_analog:
				# there was no analog pulse file with the specified combo of regex + ext found in the folder
				# in this case, the glob only contains at most one other file with the chosen extension, so take it

				if len(analog_pulse_glob) > 1:
					print("the day has come! length of analog pulse glob is > 1 when looking for a backup file from the other nsp. Edit code to handle this case.")
					exit(-10)

				found_file = analog_pulse_glob[0]

				filesize = os.path.getsize(found_file)
				session_fileset["analog_pulse"] = found_file.split("/")[-1]
				session_fileset["analog_pulse_filesize"] = filesize

		if digital_pulse != "None" and digital_pulse_glob != []:

			for found_file in digital_pulse_glob:

				if current_sess_inclusion_str in found_file:
					if current_sess_exclusion_str is "None" or (current_sess_exclusion_str is not "None" and current_sess_exclusion_str not in found_file):

						filesize = os.path.getsize(found_file)
						session_fileset["digital_pulse"] = found_file.split("/")[-1]
						session_fileset["digital_pulse_filesize"] = filesize

			if session_fileset["digital_pulse"] == "" and use_backup_digital:
				# there was no digital pulse file with the specified combo of regex + ext found in the folder
				# in this case, the glob is non-empty and only contains at most one other file with the chosen extension, so take it

				if len(digital_pulse_glob) > 1:
					print(digital_pulse_glob)
					print("the day has come! length of digital pulse glob is > 1 when looking for a backup file from the other nsp. Edit code to handle this case.")
					exit(-10)

				found_file = digital_pulse_glob[0]

				filesize = os.path.getsize(found_file)
				session_fileset["digital_pulse"] = found_file.split("/")[-1]
				session_fileset["digital_pulse_filesize"] = filesize

		session_fileset.update({"session_filesize":  session_fileset["ns6_filesize"] + session_fileset["ns5_filesize"] + session_fileset["analog_pulse_filesize"] + session_fileset["digital_pulse_filesize"]})
		recording_filesets.append(session_fileset)

recording_filesets = sorted(recording_filesets, key=takeDate)

input_filesets = [ s for s in recording_filesets if s["session_filesize"] != 0 ]
input_session_size = sum([ s["session_filesize"] for s in input_filesets ])
input_session_names = [ s["session_name"] for s in input_filesets ]

########################################################################################################
########################################################################################################

if dry_run:

	print("found the following files")

	for sess in input_filesets:
		print(sess["session_name"] + " ( " + str(sess["session_filesize"]/1e9) + " Gb )")

	print()

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
new_batch.write("#transfer sess count: " + str(transfer_count) + "\n")
new_batch.write("\n\n")

for sess in current_upload_list:

	subj = sess["subj"]

	sess_elementInfo_fname = sess_info_temp_dir + "/" + sess["session_name"] + "_elementInfo.txt"
	sess_elementInfo_file = open(sess_elementInfo_fname, 'w')
	sess_elementInfo_file.write(sess["channel_string"])
	sess_elementInfo_file.close()

	new_batch.write(sess_elementInfo_fname)
	new_batch.write(" ")
	new_batch.write(biowulf_dest_path + "/" + sess["session_name"] + "/" + sess["session_name"] + "_elementInfo.txt")
	new_batch.write("\n")

	if sess["ns6"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["ns6"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + sess["session_name"] + "/" + sess["session_name"] + ".ns6")
		new_batch.write("\n")

	if sess["ns5"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["ns5"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + sess["session_name"] + "/" + sess["session_name"] + ".ns5")
		new_batch.write("\n")

	if sess["analog_pulse"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["analog_pulse"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + sess["session_name"] + "/" + sess["session_name"] + "." + sess["analog_pulse"][-3:])
		new_batch.write("\n")

	if sess["digital_pulse"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["digital_pulse"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + sess["session_name"] + "/" + sess["session_name"] + "." + digital_pulse)
		new_batch.write("\n")

	sess_info_fname = sess_info_temp_dir + "/" + sess["session_name"] + "_info.txt"
	sess_info_file = open(sess_info_fname, 'w')
	sess_info_file.write(sess["session_info_str"])
	sess_info_file.close()

	new_batch.write(sess_info_fname)
	new_batch.write(" ")
	new_batch.write(biowulf_dest_path + "/" + sess["session_name"] + "/" + sess["session_name"] + "_info.txt")
	new_batch.write("\n")

new_batch.close()

print("\n\n")
print("biowulf_dest_path: " + biowulf_dest_path)
print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  -- MAKE SURE THIS IS RIGHT\n\n")
print('\n\n')

print("next run 'bash input_transfer.sh' (or look inside input_batch.txt to make sure you included all the files you wanted)")
