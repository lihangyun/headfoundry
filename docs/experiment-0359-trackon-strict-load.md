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

## Actual result

Preregisteredc9300e0. Dependency install35.938s/117116928bytes observed process-tree
peak; architecture load15.218s/685813760bytes. CPU Torch2.8.0, Transformers4.56.1,
safetensors0.6.2, NumPy2.2.6; full observed25-package inventory in private report,
added15packages frozen in examples/trackon-0359-load-requirements.txt after
resolution. Main environment unchanged. No timm, torchvision, stock MMCV,
training/evaluation package, DINOv3 or NC coordinate source imported.

Both weights verified before model construction; local config verified.
Separate strict DINOv2 load succeeded, then tracker509 + backbone223 =732state
entries matched complete architecture: zero missing, extra or mismatched shapes.
Strict merged loading succeeded and every loaded tensor equals its supplied
value exactly. No random missing-prefix exception used. Socket connect denied
and HF/Transformers offline flags set (in-process guard, not OS sandbox).

Private assets/private/trackon-load-0359 contains adapted source with source/
adapted hashes and license notices, load-result.json and install/check receipts.
This includes parameter-free state-independent construction; it does not prove
forward output semantics. `indices_to_coords` deliberately raises if invoked,
as does any attempted nonzero DropPath. The pinned backbone has zero drop-path.
These are explicit load-only restrictions, not substitute inference algorithms.
No call to model.forward/extract_frame_features/track_frame occurred.

167shared tests pass8.954s. Status TECHNICAL_CHECK_PASSED for strict state loading
only. Next required work: independently implement and verify coordinate
conventions, then one bounded owned-fixture forward/control before patient
camera experiment. Human reconstruction and medical accuracy remain UNVERIFIED.
