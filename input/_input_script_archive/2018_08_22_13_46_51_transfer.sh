#!/usr/bin/bash

if [ ! -d /data/zaworaca/data/ME/NIH050_utah//Volumes/56B/UTAH_B/NIH050/data_raw/170629_1025_beh/170629_1025_utah_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/ME/NIH050_utah//Volumes/56B/UTAH_B/NIH050/data_raw/170629_1025_beh/170629_1025_utah_beh
fi
if [ ! -d /data/zaworaca/data/ME/NIH050_utah//Volumes/56B/UTAH_B/NIH050/data_raw/170705_1031_beh/170705_1031_utah_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/ME/NIH050_utah//Volumes/56B/UTAH_B/NIH050/data_raw/170705_1031_beh/170705_1031_utah_beh
fi
globus transfer 32749cf0-0537-11e8-a6a1-0a448319c2f8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_08_22_13_46_51 transfer-2" < input_batch.txt