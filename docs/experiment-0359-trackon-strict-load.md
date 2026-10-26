# 0359 strict offline architecture loading

2026-10-26. Software admission only, not a physical trial. Reuse0356 captured
MIT inference modules, inherited Apache2 adapter notice,0357 tested explicit
operator and0358 verified weights. Do not import stock predictor/evaluation,
NC-derived coordinate helper or DINOv3. Remove unused torchvision imports only
after static name-use checks. Replace timm initializer with torch.nn.init's
same trunc_normal_ API; nonzero DropPath and coordinate calls fail closed in
this load-only stage, so no invented coordinate convention is exercised.

Use Transformers4.56.1 (upstream declared version, Apache2) and
safetensors0.6.2; construct Dinov2Model from pinned local config and require
strict backbone state loading. Merge tracker with separately verified backbone
and require exact key/shape coverage, then strict model loading. No missing-key
prefix exception, unsafe pickle, AutoModel network loading or inference.
Budget: dependency installation600s/4GiB, architecture check120s/2GiB.
Ordinary packaging corrections allowed; no threshold/model/weight swaps.
Success proves loading only. Actual coordinate helper, forward execution,
physical controls and camera/medical accuracy remain separate unpassed gates.
