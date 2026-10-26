# 0358 pinned asset inspection

2026-10-26; builds on0356 identities and0357 successful operator control.
Scope: download the two exact publicly accessible commercially licensed weight
files, verify sizes/SHA256, inspect tensors safely without executing a model.
No patient inputs, training, geometry, changes to physical gates or model forward.
Budget: download <=600s/1GiB process-tree peak; inspect <=120s/2GiB.
No alternative weights/revisions on failure. Existing verified files reused;
bad partial downloads not admitted. Use torch.load(weights_only=True), never
unsafe pickle fallback. DINOv2 safetensors header inspection uses stdlib.
Download pinned backbone config and verify its publisher Git blob identity.
Actual complete model-state coverage remains unverified until architecture load;
matching hashes or finite tensors alone cannot certify it. No full model or
patient runtime permission is granted by this stage.

## Packaging interruption and monitor correction

First download worker stopped after0.343s; log empty, no weight/config/partial
file existed. Monitor attributed29 processes/4307636224bytes to that just-created
worker. Source inspection found PPID-only ancestry incorrectly admits processes
whose original parent exited before its PID was reused. Historical creation
times were not recorded, so this explains a concrete vulnerability and probable
false attribution, not a proven identity of every process in that old receipt.
This is not a model or physical-accuracy rejection.

Fix shared monitor to require process creation at/after this launch, both for
measurement and termination; replace taskkill's unfiltered /T traversal with
verified descendant handles. Deterministic stale-parent/exited-launcher tests
pass; actual Windows worker measurement and enforced timeout pass. Existing
166tests passed8.548s before adding the live test; targeted3tests then passed
0.640s. Historical peak-memory estimates are not retroactively certified.

Authorize engineering replay `download-birthguard` with new receipt, identical
assets and original600s/1GiB limits; retain initial failure untouched. No model
has run, no physical stop condition is being relaxed. Resume inspection only
if the corrected download succeeds.

## Actual results

Corrected download completed20.110s, observed verified-age worker-tree peak
49451008bytes. Both binaries match0356 exact publisher size/SHA256; no alternative
checkpoint. Pinned DINOv2 config matches publisher Git blob5664b325e6258d3960fad8c4c1cff958f3cc2272.
Safe inspection completed5.078s, observed peak325316608bytes:
509tracker tensors /23431461elements, all finite;223backbone tensors /
22056576F32elements, contiguous valid safetensors offsets and full payload size.
Backbone numerical finiteness is not measured by header inspection. Tracker was
read with weights_only=True; no arbitrary-pickle fallback. Config says
384hidden,12layers,6heads,14patch,zero drop-path, matching the selected small model.

Evidence retained locally in `assets/private/trackon-assets-0358`: two exact
weights, config.json, tensor-inventory.json and original/corrected worker logs
and receipts. Files are not uploaded or committed. Total selected weight bytes
182150387. Full architecture/state-key coverage and forward behavior remain
UNVERIFIED; no inference, head, camera or medical scoring occurred.
167shared tests pass8.845s. Status TECHNICAL_CHECK_PASSED for asset inspection,
not reconstruction acceptance. Candidate remains active, not a failed route;
continue strict architecture loading rather than redownload/reselect weights.
