# globus_tools

Using globus_tools is the first and last step to extracting LFP's and/or spikes on biowulf. Globus is a file transfer protocol that is optimized for large amounts of data. It is ideal for moving the amount of Utah data that is often generated during a single subject's stay. Find out more about Globus and its setup [here](https://hpc.nih.gov/storage/globus.html). The scripts in this repository are designed to transfer "raw" data from FRNU56/72 onto biowulf, and then return the results.   

-----

### Transferring to biowulf

Using `input/prepare_input_transfer.py` you can transfer data, selectively by NSP, from FRNU56/72 to biowulf. It will create two output files in the `input/` folder, `input_batch.txt` and `input_transfer.sh`. Using globus command line tools, you can then run `input_transfer.sh`.

_BEFORE STARTING_:
  * make sure your source and destination computer are Globus endpoints you can access.
  * make sure their endpoint IDs are recorded in globus_ID.csv.
  * make sure you are connected to FRNU56/56A. This path is needed to store temp files.
  * and make sure you have globus command line [tools](https://docs.globus.org/cli/) installed on the computer where you will execute the transfer.
  * you need python3

###### Steps for executing input transfer

  * clone this repository
  * run `python input/prepare_input_transfer.py <source_path_to_session_folders> <destination_path> <NSP_name>`
    * ex: `python prepare_input_transfer.py /Volumes/56A/UTAH_A/NIH029 /data/zaworaca/subjs/NIH029 utah_m`
	* `<NSP_name>` references the NPS column in jacksheetBR_complete.csv. Two NSPs can be transferred at the same time by passing `NSP_name1+NSP_name2`. More detail is provided about `NSP_name` below.
  * check `input_batch.txt` to make sure things look right, and then run `input_transfer.sh`.

###### The inner guts
`input/prepare_input_transfer.py` scans all the sessions found in a subject's folders and reads their jacksheetBR_complete.csv files. It looks for micro devices (microDev != -1) found on selected NSPs, in sessions lasting longer than 5 minutes, and with a "raw" range of 10 units. The final set of sessions are included in the transfer list for biowulf.

Whereas sessions stored on FRNU56 keep both NSP filesets together, files are copied into separate session-by-NPS folders on biowulf. The filename column in jacksheetBR_complete specifies the ns5/6 file that is copied, along with any ns3 or nev files matching the NSP.

NOTE: If a session does not contain ain pulse channels or an nev file, the `--skip_backup_analog` and `--skip_backup_digital` options will dictate whether or not the respective pulse files from the partner NSP are used.

-----
### Transferring from biowulf



-----

### Typical LFP/spike order of operations

1. Use globus_tools to transfer subject data to biowulf

2. If LFPs:

  * create the jobs for submission using scripts in [`_utah_lfp_pipe_tools`](https://github.com/czawora/_utah_lfp_pipe_tools).
  * run the jobs and check for completion.


3. If spikes with mountainsort:

  * create the jobs for submission using scripts in [`_utah_ms_pipe_tools`](https://github.com/czawora/_utah_ms_pipe_tools).
  * run the jobs and check for completion.


4. Use globus_tools to transfer the results to wherever you want.
