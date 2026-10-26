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
