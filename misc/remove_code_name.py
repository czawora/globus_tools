
import sys
import os

if len(sys.argv) < 2:

    print("argument must be subj path")
    exit(1)

else:

    subj_path = sys.argv[1]

    if os.path.isdir(subj_path) is False:

        print("subj_path is not a valid directory")
        exit(1)

subj_path_ls = os.listdir(subj_path)

for idx, sess in enumerate(subj_path_ls):

    if sess != "_swarms":

        subj_name = sess.split("_")[0]

        old_sess_path_splits = sess.split("-")

        ymd = old_sess_path_splits[1]
        hms = old_sess_path_splits[2]
        nsp = old_sess_path_splits[3]

        # for idx2, sess2 in enumerate(subj_path_ls):
        #
        #     if sess2 != "_swarms":
        #
        #         subj_name2 = sess2.split("_")[0]
        #
        #         old_sess_path_splits2 = sess2.split("-")
        #
        #         ymd2 = old_sess_path_splits2[1]
        #         hms2 = old_sess_path_splits2[2]
        #         nsp2 = old_sess_path_splits2[3]
        #
        #         if idx != idx2:
        #             if ymd[2:] == ymd2[2:] and hms[:-2] == hms2[:-2] and nsp == nsp2:
        #                 print(sess)
        #                 print(sess2)
        #                 print("\n\n")

        old_sess_path = subj_path + "/" + sess
        new_sess_path = subj_path + "/" + subj_name + "_" + ymd[2:] + "_" + hms[:-2] + "_" + nsp

        print(old_sess_path + " --> " + new_sess_path)

        sess_ls = os.listdir(old_sess_path)

        for filename in sess_ls:

            if os.path.isfile(old_sess_path + "/" + filename):

                filename_noext = filename.split(".")[0]
                ext = filename.split(".")[1]

                filename_noext_splits = filename_noext.split("-")

                filename_ymd = filename_noext_splits[1]
                filename_hms = filename_noext_splits[2]
                filename_nsp = filename_noext_splits[3]

                old_fpath = old_sess_path + "/" + filename
                new_fpath = old_sess_path + "/" + subj_name + "_" + filename_ymd[2:] + "_" + filename_hms[:-2] + "_" + filename_nsp + "." + ext

                print("\t" + old_fpath + " --> " + new_fpath)

                os.rename(old_fpath, new_fpath)

        if os.path.isdir(new_sess_path) is False:
            os.rename(old_sess_path, new_sess_path)
