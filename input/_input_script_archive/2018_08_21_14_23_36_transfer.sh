#!/usr/bin/bash

if [ ! -d /data/zaworaca/data/ME/NIH050_micro/170629_1025_micro_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/ME/NIH050_micro/170629_1025_micro_beh
fi
if [ ! -d /data/zaworaca/data/ME/NIH050_micro/170705_1031_micro_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/ME/NIH050_micro/170705_1031_micro_beh
fi
globus transfer 32749cf0-0537-11e8-a6a1-0a448319c2f8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_08_21_14_23_36 transfer-2" < input_batch.txt