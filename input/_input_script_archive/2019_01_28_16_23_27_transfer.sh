#!/usr/bin/bash

globus transfer deb04de0-fe27-11e8-9345-0e3d676669f4 e2620047-6d04-11e5-ba46-22000b92c6ec --no-verify-checksum  --sync-level size  --batch --label "2019_01_28_16_23_27 transfer-182sess" < input_batch.txt