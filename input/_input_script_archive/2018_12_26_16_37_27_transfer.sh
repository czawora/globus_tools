#!/usr/bin/bash

globus transfer deb04de0-fe27-11e8-9345-0e3d676669f4 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2018_12_26_16_37_27 transfer-62sess" < input_batch.txt