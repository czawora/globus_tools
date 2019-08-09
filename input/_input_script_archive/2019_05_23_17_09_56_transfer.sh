#!/usr/bin/bash

globus transfer 45d75c5a-4beb-11e9-a61a-0a54e005f950 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_05_23_17_09_56 transfer-89sess" < input_batch.txt