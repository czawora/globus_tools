#!/usr/bin/bash

globus transfer bf6ee0da-8965-11e9-b807-0a37f382de32 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_06_10_14_40_20 transfer-270sess" < input_batch.txt