#!/usr/bin/bash

globus transfer 32749cf0-0537-11e8-a6a1-0a448319c2f8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_11_19_15_35_25 transfer-5" < input_batch.txt