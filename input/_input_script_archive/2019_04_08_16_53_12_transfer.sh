#!/usr/bin/bash

globus transfer 36f93e64-3ec7-11e9-a615-0a54e005f950 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_04_08_16_53_12 transfer-39sess" < input_batch.txt