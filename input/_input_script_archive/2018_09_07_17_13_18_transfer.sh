#!/usr/bin/bash

if [ ! -d /data/zaworaca/data/labmates/DY/NIH062/180830_1659_nsp2 ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/DY/NIH062/180830_1659_nsp2
fi
if [ ! -d /data/zaworaca/data/labmates/DY/NIH062/180830_1730_nsp2 ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/DY/NIH062/180830_1730_nsp2
fi
if [ ! -d /data/zaworaca/data/labmates/DY/NIH062/180831_1641_nsp2 ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/DY/NIH062/180831_1641_nsp2
fi
if [ ! -d /data/zaworaca/data/labmates/DY/NIH062/180831_1711_nsp2 ]; then
mkdir -p -m 777 /data/zaworaca/data/labmates/DY/NIH062/180831_1711_nsp2
fi
globus transfer 850e119a-b2e2-11e8-8240-0a3b7ca8ce66 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_09_07_17_13_18 transfer-4" < input_batch.txt