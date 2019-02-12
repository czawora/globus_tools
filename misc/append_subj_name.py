
import sys
import os

if len(sys.argv) < 4:

    print("argument 1) must be subj path")
    print("argument 2) must be pulse nsx file extension")
    print("argument 3) must be appended subj name")

    exit(1)

else:

    subj_path = sys.argv[1]
    pulse_nsx_ext = sys.argv[2]
    subj_name = sys.argv[3]

    if os.path.isdir(subj_path) is False:

        print("subj_path is not a valid directory")
        exit(1)

subj_path_ls = os.listdir(subj_path)

for sess in subj_path_ls:

    if sess != "_swarms":

        sess_path = subj_path + "/" + sess
        sess_ls = os.listdir(sess_path)

        for filename in sess_ls:

            if filename[-3:] == "nev" or filename[-3:] == pulse_nsx_ext:

                print(filename + " --> " + subj_name + "_" + filename)

                old_fpath = sess_path + "/" + filename
                new_fpath = sess_path + "/" + subj_name + "_" + filename
                os.rename(old_fpath, new_fpath)
