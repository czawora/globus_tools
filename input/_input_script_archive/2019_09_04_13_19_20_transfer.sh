#!/usr/bin/bash

globus transfer 68df8464-cf23-11e9-939e-02ff96a5aa76 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_09_04_13_19_20 transfer-33sess" < input_batch.txt