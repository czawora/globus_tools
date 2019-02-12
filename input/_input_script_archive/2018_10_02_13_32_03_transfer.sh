#!/usr/bin/bash

if [ ! -d /data/zaworaca/data/labmates/JW_rush/NIH064/180926_1517_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/JW_rush/NIH064/180926_1517_beh
fi
if [ ! -d /data/zaworaca/data/labmates/JW_rush/NIH064/180927_1112_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/JW_rush/NIH064/180927_1112_beh
fi
if [ ! -d /data/zaworaca/data/labmates/JW_rush/NIH064/180928_1121_beh ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/JW_rush/NIH064/180928_1121_beh
fi
globus transfer 32749cf0-0537-11e8-a6a1-0a448319c2f8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_10_02_13_32_03 transfer-3" < input_batch.txt