# globus_tools

how to create LFPs and Mountainsort spikes for a subject

step 1: get the subject's data onto biowulf

- clone the git repo 'globus_tools'
- find a directory for this repo and run 'git clone https://github.com/czawora/globus_tools.git'

- enter the /input directory and run 'python3 prepare_input_transfer.py' to see the options (ignore prepare_input_transfer_csv.py)

- once you run prepare_input_transfer.py with the desired inputs, inspect input_batch.txt and input_transfer.sh to double check your inputs performed as expected
(in order to run lfp extraction and mountainsort according to this guide, you must transfer your data somewhere into /data/FRNU)

- run input_transfer.sh , then check the transfer on the globus website to make sure the tranfer is underway without a problem
(common problems are: either endpoint, FRNU or NIH_Globus, is not activated, or the FRNU endpoint does not have source drive on it's access list)

- depending on the data size, your data will now appear on biowulf

step 2: prepare and run the mountainsort scripts

- the relevant scripts for this step exist in /data/FRNU/python_scripts/_utah_ms_pipe_tools
- cd into that directory

- to create the necessary lfp scripts for each session in a subject dir, run 'python3 construct_bash_scripts.py [path_to_subj_dir]'
- once it completes, run the swarm file created in [path_to_subj_dir]/_swarms/sort_initial_swarm.sh

- later on, to check if your jobs are still running, run 'sjobs'
- when you see that all your jobs have completed, you can check the completion status of each session by running /data/FRNU/python_scripts/_utah_ms_pipe_tools/tally_sessions.py


step 3: prepapre and run the lfp scripts

- the relevant scripts for this step exist in /data/FRNU/python_scripts/_utah_lfp_pipe_tools
- cd into that directory

- to create the necessary lfp scripts for each session in a subject dir, run 'python3 construct_lfp_bash_scripts.py [path_to_subj_dir]'
- once it completes, run the swarm file created in [path_to_subj_dir]/_swarms/lfp_initial_swarm.sh

- later on, to check if your jobs are still running, run 'sjobs'
- when you see that all your jobs have completed, you can check the completion status of each session by running /data/FRNU/python_scripts/_utah_ms_pipe_tools/tally_lfp.py


step 4: return the outputs of lfp, sorts, or both to an FRNU location

- use prepare_input_transfer.py in the globus_tools/output dir
