#!/usr/bin/bash

globus transfer 6b294e82-5a41-11e9-9e6e-0266b1fe9f9e e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_04_10_13_53_19 transfer-88sess" < input_batch.txt