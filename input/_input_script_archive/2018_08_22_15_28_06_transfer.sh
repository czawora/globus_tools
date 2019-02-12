#!/usr/bin/bash

if [ ! -d /data/zaworaca/data/ME/NIH053_micro/171006_1125_micro ]; then
mkdir -p -m 777 /data/zaworaca/data/ME/NIH053_micro/171006_1125_micro
fi
globus transfer 32749cf0-0537-11e8-a6a1-0a448319c2f8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_08_22_15_28_06 transfer-1" < input_batch.txt