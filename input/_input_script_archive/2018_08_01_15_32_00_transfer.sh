#!/usr/bin/bash

if [ ! -d /data/zaworaca/data/NIH059/180331_1147_utah ]; then
mkdir -p -m 777 /data/zaworaca/data/NIH059/180331_1147_utah
fi
if [ ! -d /data/zaworaca/data/NIH059/180402_1626_utah ]; then
mkdir -p -m 777 /data/zaworaca/data/NIH059/180402_1626_utah
fi
globus transfer 32749cf0-0537-11e8-a6a1-0a448319c2f8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_08_01_15_32_00 transfer-2" < input_batch.txt