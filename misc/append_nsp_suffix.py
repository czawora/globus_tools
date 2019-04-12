
import glob
import sys
import os

subj_path = sys.argv[1]
append_str = sys.argv[2]
testrun = sys.argv[3]

jacksheet_glob = glob.glob(subj_path + "/*/*jacksheet*")

subj_sessions = list(set(["/".join(l.split("/")[0:-1]) for l in jacksheet_glob]))

for sess in subj_sessions:

	print(sess + " --> " + sess + "_" + append_str)

	if testrun == "1":
		os.rename(sess, sess + "_" + append_str)
