#!/usr/bin/bash

globus transfer 94a7d578-944b-11e9-bf5b-0e4a062367b8 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_08_19_12_35_07 transfer-101sess" < input_batch.txt