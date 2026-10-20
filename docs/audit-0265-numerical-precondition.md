# Audit0265: numerical precondition, not another model trial

Date:2026-10-20. User explicitly permits a precondition-design audit and temporary
retention of public weights. This does **not** authorize a model rerun, threshold
change, new route, training or upload. Original0264 remains REJECT; physical
accuracy remains UNVERIFIED. Source recovery before this audit:1eae618.

## Bounded audit registration

Start:2026-10-20T08:54:51.705Z;stop by09:14:51.705Z including documentation and
checks. Single question:does the registered uniform atol/rtol1e-6 comparison
provide a justified inference about physical3px/2mm quality? Hypothesis:it is
an implementation-consistency diagnostic,not a calibrated reconstruction gate.

Read only existing source,small logs and official Torch2.10 documentation. Tiny
synthetic arithmetic is permitted;no model/checkpoint load,forward,patient-image
or scan read,case002 access,rendering or asset download. No new dependency or
production/default change. Stop if existing evidence cannot resolve the failing
head or numerical cause;do not rerun to recover missing evidence. Record unknowns
instead. Preserve original logs,archive and unrelated0207. Temporarily retain
the public checkpoint,lossless derived weights and isolated runtime;do not call
this a completed failed-route cleanup or model acceptance.

## Findings

1. `tools/check_opend4rt_3d_0264.py:258-264` compares nine queries with three
   groups of three,using the same cached encoder memory. It applies the identical
   `abs(actual-expected) <= 1e-6 + 1e-6*abs(expected)` condition to six semantically
   different heads. `expected` is the chunked result,not physical ground truth.
   No derivation connects this tolerance to3px,1px p95 or2mm. The earlier tiny
   fixture checks storage/execution,but its observed delta is not an error bound
   for the full1162433293-parameter network.
2. All16 pinned upstream source/license hashes still match the0262 lock. Static
   source has per-query embedding,query-to-memory cross attention and per-token
   heads;no query self-attention. Loading returns `eval().requires_grad_(False)`;
   inference uses `inference_mode()`. Thus query grouping is mathematically
   independent in this path,while finite-precision evaluation order can differ.
   This is a source-level explanation of plausibility,not a measured root cause
   or proof all operations are deterministic. No extra initializer is enabled.
3. Torch2.10 explicitly warns that batch/slice operations need not give identical
   floating-point results. Its generic FP32 testing defaults are atol1e-5 and
   rtol1.3e-6,not a model-specific or physical guarantee. **Do not switch to those
   defaults as a post-hoc fix** or infer this unknown head would be acceptable.
4. Important correction to the shorthand in0264/README:the diagnostic reports
   the largest absolute/relative differences **among mismatched components**.
   Both the installed `_comparison.py:320-328` and pinned officialv2.10.0 source
   zero matching entries before calculating these maxima. Therefore1.66893e-6
   is not established as the maximum over all27 components,all heads or the
   full model. Three mismatched scalar components are not three failed points.
5. Raw arrays,head name and completed physical metrics were not persisted before
   the assertion. XYZ,displacement and normal all have three components. Their
   numerical meaning is different;XYZ has no established millimeter scale until
   the frozen proper Sim3 evaluation. Relative deltas alone cannot bound physical
   error or alignment conditioning. Missing evidence cannot be recovered by
   reading an exception message. No model rerun was made to fill this gap.
6. Nine-versus-three is not a certificate for the actual512-query schedule or all
  2355 points/32 frames. Consistency can pass for equally wrong predictions;very
   small logit changes can flip visibility at zero. Conversely,a normalized UV
   difference can fail1e-6 while remaining far below one pixel. These are distinct
   questions and must not be collapsed into one blanket tensor comparison.

Primary sources,checked2026-10-20:

- [Torch2.10 numerical accuracy](https://docs.pytorch.org/docs/2.10/notes/numerical_accuracy.html#batched-computations-or-slice-computations)
- [Torch2.10 assert_close formula/defaults](https://docs.pytorch.org/docs/2.10/testing.html#torch.testing.assert_close)
- [Pinned Torchv2.10.0 mismatch reporter](https://github.com/pytorch/pytorch/blob/v2.10.0/torch/testing/_comparison.py#L310-L328)

## Synthetic arithmetic checks,not a reconstruction result

Five deterministic standard-library witnesses pass without importing Torch,
loading a model or reading human materials. They check:FP32 non-associativity;
an uncalibrated UV tolerance;identically wrong outputs;visibility sign flips;
and mismatch-only versus whole-array maxima. Exact code/output and small source
hashes are recorded in `assets/private/numerical-precondition-audit-0265/`.

For illustration only,if each UV component differed by the logged value,the
719/639 native extents would give0.00160537px. **The failed head was not identified
as UV;this is not the observed model pixel error.** A separate synthetic pair
has a matching component differing by0.5 but the reported mismatch maximum only
1.66893e-6. A visibility logit pair[-2e-7,+2e-7] passes the old numerical formula
while changing its discrete call. None of these witnesses diagnoses the model.

Replay the saved arithmetic without a model/runtime dependency:

```powershell
cd C:/workspace/headfoundry
@'
import json
from pathlib import Path
r = json.loads(Path('assets/private/numerical-precondition-audit-0265/arithmetic-replay.json').read_text())
exec(r['code'])
'@ | .venv/Scripts/python.exe -B -
```

## Decision and next boundary

Audit conclusion:the uniform1e-6 condition is an **uncalibrated implementation
diagnostic**,not sufficient evidence for a physical reconstruction rejection.
It is also not proven to be a harmless false alarm. Original0264 stays REJECT
under its registered recipe;full3D/real cameras/head quality stay UNVERIFIED.
No gate is changed and no old failure is relabeled as passed.

Temporary public-weight retention is now explicitly authorized,not indefinite
acceptance of a failed integration. Existing original13950006682-byte checkpoint,
derived4649733172-byte payload and isolated runtime remain in place. This audit
checks their existence/size,not another full-byte integrity rehash. Original
failure/archive and successful small fixtures remain unchanged. No asset was
deleted or downloaded;no new route or process was started.

Recommended **future,not authorized by this audit**:one bounded capacity trial
with the exact same source,checkpoint,FP32,inputs,population and canonical512
schedule. Preserve strict byte/state/finite/resource checks. Persist all head
names,raw control tensors,mode/query IDs and diagnostic differences before any
stop. Numerical batching evidence must not silently replace physical truth;
either justify its separate error budget in downstream units before running,
or explicitly limit conclusions to the fixed canonical schedule and report
batch sensitivity without claiming arbitrary-batch equivalence. Do not choose
a tolerance from the failed value or try precision/chunk/checkpoint sweeps.

Such a trial needs separate authorization and prospective registration;0264's
budget cannot be reopened. Keep the physical gates exactly unchanged:all31
non-query frames/all true-visible initialized IDs;p95<=1px,max<=3px;visible and
occluded recalls>=.95;finite outputs/positive required depth;one all-point
frame0 proper positive Sim3 frozen across frames and point p95<=2mm. Full0237
surface/camera/full-head/ears/neck/editability and actual human visual acceptance
are still later gates,not granted by a capacity check. A failed physical trial
must close and clean its exclusive integration before changing route.

## Verification and closeout

All133 shared tests pass in4.698s;the five arithmetic witnesses also pass. These
are technical checks,not model/head acceptance. Original small inference/source
evidence hashes are unchanged;the previous0264 archive remains731648bytes with
61 members,CRC passing and SHA256
`3ff549df69074ee087fa60f314ac58dcabd5d5561cd16210911a085ca97fc973`.
Git changes are documentation only;shared implementation,active runner/locks,
production defaults and unrelated0207 remain untouched. No model job is active.
Audit evidence/result and the resolved choice are saved locally;the original
pending-choice record remains historical,not the current authorization state.
This closes the audit,not the overall reconstruction goal or failed-route cleanup.
