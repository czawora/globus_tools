#!/usr/bin/python3

import os
import datetime
import argparse
import glob
import re
import csv
from random import sample

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

parser = argparse.ArgumentParser(description = 'build list of dir + files to transfer to biowulf, also write transfer script')

parser.add_argument('subj_path')
parser.add_argument('biowulf_dest_path')
parser.add_argument('--fname_regex_include', default = '.*')
parser.add_argument('--fname_regex_exclude', default = '#')
parser.add_argument('--raw_dir', default = 'data_raw')
parser.add_argument('--sesslist', default = "")

parser.add_argument('--ns5', action='store_true')
parser.add_argument('--ns6', action='store_true')

parser.add_argument('--analog_pulse', default = 'ns3', nargs = '?', choices = ['ns2', 'ns3', 'ns4', 'ns5', 'ns6', 'None'], help = 'which file extension in the session folder contains the analog pulses, or None to ignore')
parser.add_argument('--digital_pulse', default = 'nev', nargs = '?', choices = ['nev', 'None'], help = 'which file extension in the session folder contains the digital pulses, or None to ignore')

parser.add_argument('--dry_run', action='store_true')

parser.add_argument('--skip_backup_analog', action='store_false')
parser.add_argument('--skip_backup_digital', action='store_false')

parser.add_argument('--reference_set', default = '', nargs='+')

args = parser.parse_args()

subj_path = args.subj_path
biowulf_dest_path = args.biowulf_dest_path
fname_regex_include = args.fname_regex_include
fname_regex_exclude = args.fname_regex_exclude
raw_dir = args.raw_dir
sesslist = args.sesslist

reference_set = args.reference_set

ns5 = args.ns5
ns6 = args.ns6

analog_pulse = args.analog_pulse
digital_pulse = args.digital_pulse

use_backup_analog = args.skip_backup_analog
use_backup_digital = args.skip_backup_digital

dry_run = args.dry_run

session_path = subj_path + "/" + raw_dir

subj = subj_path.split("/")[-1]

include_re_pattern = re.compile(fname_regex_include)
exclude_re_pattern = re.compile(fname_regex_exclude)

if ns5 and ns6:
	print("only choose either ns5 or ns6, there should be no reason to need both")
	exit(2)

########################################################################################################
########################################################################################################
# make sure paths from arguments exist

if sesslist != "" and os.path.isfile(sesslist) is False:
	print("value passed as --sesslist is not a valid path")
	exit(-1)

if os.path.isdir(subj_path) is False:
	print("value passed as --subj_path is not a valid path")
	exit(-1)

ref_set_indices = []
ref_set_region_numcodes = []

for ref_set in reference_set:

	if ref_set is "" or ref_set not in micro_reference_set_name:
		print("reference_set must be a string present in the first column of this table")

		for el, idx in enumerate(micro_reference_set_name):
			print("\t".join([micro_reference_set_name[idx], micro_reference_subj[idx], micro_reference_channel_string[idx], micro_reference_channel_num_set[idx], micro_reference_array_num[idx], micro_reference_array_location[idx], micro_reference_description[idx]]))

		print()
		exit(1)

	else:
		reference_set_index = micro_reference_set_name.index(ref_set)
		implant_region_index = implant_region_names.index(micro_reference_array_location[reference_set_index])

		ref_set_region_numcodes.append(implant_region_numcode[implant_region_index])
		ref_set_indices.append(reference_set_index)

########################################################################################################
########################################################################################################
# gather list of files in raw_dir
# xpecting files folders to have dddddd_dddd.*

matching_nsp_strings = []

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
		datestring_YMD = datestring_match.split("_")[0]
		datestring_HM = datestring_match.split("_")[1]
		# good session name, check for goood filename

		current_sess_path = session_path + "/" + sess

		sess_dir_ls = os.listdir(current_sess_path)

		session_unique_filenames = list(set( [f[:-4] for f in sess_dir_ls] ))

		for f in session_unique_filenames:

			# session name can be of two types
			# 170311_0001_utah --> date_time_nsp
			# YfGGmZkGMfb-20190118-102433-INST0 --> codename-date-time-nsp
			#
			# if first one: split on "_" and append datestring_match + sess.split(end)
			# if second one: split on "-" and append datestring_match + sess.split(end)

			if "_" in f and "-" in f:
				print("underscore and hyphen present in f: " + f)
				print("splitting logic will break on this")
				print("change code needed")
				exit(1)

			if "_" in f:
				sess_name = datestring_match + "_" + "_".join(f.split("_")[2:])
			elif "-" in f:
				sess_name = datestring_match + "_" + "_".join(f.split("-")[3:])

			if ns5:

				session_info_str = "\n".join([analog_pulse, "ns5"])
			else:

				session_info_str = "\n".join([analog_pulse, "ns6"])

			session_fileset = {}

			session_fileset.update({"date_YMD": datestring_YMD})
			session_fileset.update({"date_HM": datestring_HM})

			session_fileset.update({"session_path": current_sess_path})
			session_fileset.update({"session_name": sess_name})
			session_fileset.update({"session_info_str": session_info_str})

			session_fileset.update({"ns6": ""})
			session_fileset.update({"ns6_filesize": 0})

			session_fileset.update({"ns5": ""})
			session_fileset.update({"ns5_filesize": 0})

			session_fileset.update({"analog_pulse_src": ""})
			session_fileset.update({"analog_pulse_dest": ""})
			session_fileset.update({"analog_pulse_filesize": 0})

			session_fileset.update({"digital_pulse_src": ""})
			session_fileset.update({"digital_pulse_dest": ""})
			session_fileset.update({"digital_pulse_filesize": 0})

			# for debugging
			session_fileset.update({"current_sess_unique_string": f})
			session_fileset.update({"sess_unique_list": session_unique_filenames})
			session_fileset.update({"id": id_counter})
			id_counter += 1

			if re.match(include_re_pattern, f) is not None and re.match(exclude_re_pattern, f) is None:

				matching_nsp_strings.append(f)

				ns6_glob = glob.glob(current_sess_path + "/*.ns6")
				ns5_glob = glob.glob(current_sess_path + "/*.ns5")
				analog_pulse_glob = glob.glob(current_sess_path + "/*." + analog_pulse)
				digital_pulse_glob = glob.glob(current_sess_path + "/*." + digital_pulse)

				if ns6 and ns6_glob != []:

					for found_file in ns6_glob:

						if re.match(include_re_pattern, found_file) != None and re.match(exclude_re_pattern, found_file) == None:

							filesize = os.path.getsize(found_file)
							session_fileset["ns6"] = found_file.split("/")[-1]
							session_fileset["ns6_filesize"] = filesize

				if ns5 and ns5_glob != []:

					for found_file in ns5_glob:

						if re.match(include_re_pattern, found_file) != None and re.match(exclude_re_pattern, found_file) == None:

							filesize = os.path.getsize(found_file)
							session_fileset["ns5"] = found_file.split("/")[-1]
							session_fileset["ns5_filesize"] = filesize

				if analog_pulse != "None" and analog_pulse_glob != []:

					for found_file in analog_pulse_glob:

						if re.match(include_re_pattern, found_file) != None and re.match(exclude_re_pattern, found_file) == None:

							filesize = os.path.getsize(found_file)
							session_fileset["analog_pulse_src"] = found_file
							session_fileset["analog_pulse_dest"] = sess_name + "." + analog_pulse
							session_fileset["analog_pulse_filesize"] = filesize

					if session_fileset["analog_pulse_src"] is "" and use_backup_analog:
						# there was no analog pulse file with the specified combo of regex + ext found in the folder
						# in this case, the glob only contains at most one other file with the chosen extension, (assuming only 2 NSPs) so take it

						if len(analog_pulse_glob) > 1:
							print("the day has come! length of analog pulse glob is > 1 when looking for a backup file from the other nsp. Edit code to handle this case.")
							exit(-10)

						found_file = analog_pulse_glob[0]

						if "_" in found_file and "-" in found_file:
							print("underscore and hyphen present in found_file: " + found_file)
							print("splitting logic will break on this")
							print("change code needed")
							exit(1)

						if "_" in found_file:
							renamed_found_file = datestring_match + "_" + "_".join(found_file.split("_")[2:])
						elif "-" in found_file:
							renamed_found_file = datestring_match + "_" + "_".join(found_file.split("-")[3:])

						filesize = os.path.getsize(found_file)
						session_fileset["analog_pulse_src"] = found_file
						session_fileset["analog_pulse_dest"] = renamed_found_file
						session_fileset["analog_pulse_filesize"] = filesize

						print("using analog pulse file from other nsp ** " + session_fileset["analog_pulse_src"] + " --> " + session_fileset["analog_pulse_dest"])

				if digital_pulse is not "None" and digital_pulse_glob != []:

					for found_file in digital_pulse_glob:

						if re.match(include_re_pattern, found_file) is not None and re.match(exclude_re_pattern, found_file) is None:

							filesize = os.path.getsize(found_file)
							session_fileset["digital_pulse_src"] = found_file
							session_fileset["digital_pulse_dest"] = sess_name + "." + digital_pulse
							session_fileset["digital_pulse_filesize"] = filesize

					if session_fileset["digital_pulse_src"] is "" and use_backup_digital:
						# there was no digital pulse file with the specified combo of regex + ext found in the folder
						# in this case, the glob is non-empty and only contains at most one other file with the chosen extension, so take it

						if len(digital_pulse_glob) > 1:
							print("the day has come! length of digital pulse glob is > 1 when looking for a backup file from the other nsp. Edit code to handle this case.")
							exit(-10)

						found_file = digital_pulse_glob[0]

						if "_" in found_file and "-" in found_file:
							print("underscore and hyphen present in found_file: " + found_file)
							print("splitting logic will break on this")
							print("change code needed")
							exit(1)

						if "_" in found_file:
							renamed_found_file = datestring_match + "_" + "_".join(found_file.split("_")[2:])
						elif "-" in found_file:
							renamed_found_file = datestring_match + "_" + "_".join(found_file.split("-")[3:])

						filesize = os.path.getsize(found_file)
						session_fileset["digital_pulse_src"] = found_file
						session_fileset["digital_pulse_dest"] = renamed_found_file
						session_fileset["digital_pulse_filesize"] = filesize

						print("using digital pulse file from other nsp ** session_fileset" + ["digital_pulse_src"] + " --> " + session_fileset["digital_pulse_dest"])

			session_fileset.update({"session_filesize":  session_fileset["ns6_filesize"] + session_fileset["ns5_filesize"]} )
			session_fileset.update({"session_concat_string": session_fileset["ns6"] + session_fileset["ns5"] + session_fileset["digital_pulse_src"] + session_fileset["analog_pulse_src"]})

			recording_filesets.append(session_fileset)


recording_filesets = sorted(recording_filesets, key=takeDate)

empty_filesets = [s for s in recording_filesets if s["session_filesize"] == 0]

input_filesets = [s for s in recording_filesets if s["session_filesize"] != 0]
input_session_size = sum([s["session_filesize"] for s in input_filesets])
input_session_names = [s["session_name"] for s in input_filesets]

print("num filesets: " + str(len(input_filesets)))
# remove filesets that include all the same files
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
new_batch.write("#regex_include: " + fname_regex_include + "\n")
new_batch.write("#regex_exclude: " + fname_regex_exclude + "\n")
new_batch.write("#raw_dir: " + raw_dir + "\n")
new_batch.write("#ns6: " + str(ns6) + " | ns5: " + str(ns5) + " | analog pulse: " + analog_pulse + " | digital pulse: " + digital_pulse + "\n")
new_batch.write("#transfer sess count: " + str(transfer_count) + "\n")
new_batch.write("\n\n")

for sess in current_upload_list:

	elementInfo_fpath = sess_info_temp_dir + "/" + subj + "_" + sess["session_name"] + "_elementInfo.txt"
	elementInfo_f = open(elementInfo_fpath, 'w')

	for idx, ref_set in enumerate(reference_set):

		reference_set_index = ref_set_indices[idx]
		current_implant_region_numcode = ref_set_region_numcodes[idx]

		elementInfo_f.write("\"" + "\",\"".join([micro_reference_set_name[reference_set_index], micro_reference_subj[reference_set_index], micro_reference_channel_string[reference_set_index], micro_reference_channel_num_set[reference_set_index], micro_reference_array_num[reference_set_index], current_implant_region_numcode, micro_reference_description[reference_set_index]]) + "\"\n")

	elementInfo_f.close()

	new_batch.write(elementInfo_fpath)
	new_batch.write(" ")
	new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + "_elementInfo.txt")
	new_batch.write("\n")

	if sess["ns6"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["ns6"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + ".ns6")
		new_batch.write("\n")

	if sess["ns5"] != "":

		new_batch.write(sess["session_path"] + "/" + sess["ns5"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + ".ns5")
		new_batch.write("\n")

	if sess["analog_pulse_src"] != "":

		new_batch.write(sess["analog_pulse_src"])
		# new_batch.write(sess["session_path"] + "/" + sess["analog_pulse"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["analog_pulse_dest"])
		# new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + "." + analog_pulse)
		new_batch.write("\n")

	if sess["digital_pulse_src"] != "":

		new_batch.write(sess["digital_pulse_src"])
		# new_batch.write(sess["session_path"] + "/" + sess["digital_pulse"])
		new_batch.write(" ")
		new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["digital_pulse_dest"])
		# new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + "." + digital_pulse)
		new_batch.write("\n")

	sess_info_file = open(sess_info_temp_dir + "/" + subj + "_" + sess["session_name"] + "_info.txt", 'w')
	sess_info_file.write(sess["session_info_str"])
	sess_info_file.close()

	new_batch.write(sess_info_temp_dir + "/" + subj + "_" + sess["session_name"] + "_info.txt")
	new_batch.write(" ")
	new_batch.write(biowulf_dest_path + "/" + subj + "_" + sess["session_name"] + "/" + subj + "_" + sess["session_name"] + "_info.txt")
	new_batch.write("\n")

new_batch.close()

print()
print("debug check, random sample of strings that passed regex filters:")
print(sample(matching_nsp_strings, min(len(matching_nsp_strings), 30)))

print("\n\n")
print("biowulf_dest_path: " + biowulf_dest_path)
print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  -- MAKE SURE THIS IS RIGHT\n\n")
print('\n\n')

print("next run 'bash input_transfer.sh' (or look inside input_batch.txt to make sure you included all the files you wanted)")
