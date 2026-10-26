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
