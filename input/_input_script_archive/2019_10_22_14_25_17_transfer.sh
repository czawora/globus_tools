#!/usr/bin/bash

globus transfer 68df8464-cf23-11e9-939e-02ff96a5aa76 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_10_22_14_25_17 transfer-60sess" < input_batch.txt