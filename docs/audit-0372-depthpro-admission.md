# 0372 DepthPro source and asset admission audit

2026-10-27. Public source/metadata only; no weights,inference,patient data or
runtime installation. Goal remains incomplete. Independent0371math is retained.

Git remote HEAD pinned9e65e4dbe9568d23c546fcec53302b10445e109e.
Seven small source/license documents saved with SHA256 in
assets/public/depthpro-source-audit-0372/manifest.json. Not a complete install.
Official [GitHub README](https://github.com/apple/ml-depth-pro/blob/9e65e4dbe9568d23c546fcec53302b10445e109e/README.md)
states code and weights share LICENSE. That permissive copyright grant is not
a patent grant; notices/trademark restrictions apply. ACKNOWLEDGEMENTS lists
timm/DINOv2 Apache2. These do not establish every installed dependency's rights.

## Critical conflicting model terms: do not install

Official [HF model](https://huggingface.co/apple/DepthPro) identifies apple-amlr.
Its [LICENSE](https://huggingface.co/apple/DepthPro/raw/main/LICENSE), read live,
restricts use to noncommercial research and explicitly excludes product
development. Therefore HF checkpoint admission is REJECT for this project.
The GitHub text alone must not silently override contradictory asset-specific
terms. CDN weight access cannot currently establish an alternative artifact:
curl and Python TLS handshakes both failed, no bytes downloaded or hash found.
GitHub/CDN commercial checkpoint eligibility remains UNVERIFIED, not approved.
No random mirror, older weight assumption, research-only workaround or remote
inference service is permitted. Earlier0366's source-level candidate status
must not be read as current checkpoint commercial clearance.

This also corrects this turn's preliminary statement that the shared GitHub
license sufficed: it was made before reading the conflicting HF asset terms.
No installation or inference occurred between the statement and correction.

## Technical findings retained without using the checkpoint

The inspected [infer implementation](https://github.com/apple/ml-depth-pro/blob/9e65e4dbe9568d23c546fcec53302b10445e109e/src/depth_pro/depth_pro.py)
returns reciprocal clamped canonical inverse depth scaled by W/f. Thus its
metric depth and predicted focal are coupled, not independent observations.
It internally resizes to1536square then resizes inverse depth back before
reciprocal; reordering those operations changes values. Future permitted
sources need explicit axial-versus-ray depth,units,resizing and clipping
contracts. The code alone does not empirically establish axial accuracy.
Choosing f=W would yield reciprocal canonical depth, not measured metric
scale; it would not make a restricted checkpoint lawful.

Main environment has NumPy2; candidate requiresnumpy<2 plusTorch/Torchvision/
timm/pillow_heif/matplotlib. No downgrade was made. GPU read-only inventory:
RTX3070,8192MiB total,6509MiB free at check; runtime fit remains UNVERIFIED.
Latency claims in papers are not a promise for this machine.

Decision: exclude this HF asset and stop integration before downloads. Keep
the small successful provenance audit, not a failed model/runtime. There is
no model-specific environment,weight,test output or generated mesh to clean.
Next source screening must resolve checkpoint-specific commercial rights first;
only then consider bounded inference. Do not discard independently developed
distance/measurement solver strengths because this candidate fails rights.
