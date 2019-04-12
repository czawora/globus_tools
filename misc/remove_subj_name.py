import glob
import sys
import os

subj_path = sys.argv[1]
testrun = sys.argv[2]

nih_glob = glob.glob(subj_path + "/NIH*")

for sess in nih_glob:

	current_session_name = sess.split("/")[-1]

	new_session_name = "_".join(current_session_name.split("_")[1:])

	print(subj_path + "/" + current_session_name + " --> " + subj_path + "/" + new_session_name)

	if testrun == "1":
		os.rename(subj_path + "/" + current_session_name, subj_path + "/" + new_session_name)
