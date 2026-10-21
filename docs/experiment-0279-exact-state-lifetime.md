# Experiment0279: exact-state checkpoint lifetime,unchanged physical test

Registered2026-10-21T07:01:11Z,before installing/loading/forward. Whole2400s
including implementation,assets,one forward,scoring and closeout.0278 is
resourceREJECT and fully cleaned at2b817d1;this does not reverse that result.
Current head/camera/medical/visual acceptance remainsUNVERIFIED.

## Evidence and single engineering variable

0278 passes complete946-state-item loading at3.728GB peak but the first default
forward exceeds its8GiB cap before a prediction. Its worker keeps both mapped
checkpoint dictionaries live with fully copied model parameters until after
forward. Their tensor payload is about1.663GB;the actual resident saving is not
yet measured. Source uses default copying load_state_dict,not assign=True.

Main variable:release the duplicate checkpoint objects after full strict loaded-
state validation and replace retained-dictionary postchecking by streaming exact
state fingerprints. This changes storage lifetime,not learned values,network
architecture,precision,batch/input/default resolution,thresholds or cap. It is
a materially justified resource-isolation experiment,not a model/solver sweep.
One rewrite only;failure stops without another memory/precision/resolution rescue.

Reuse0278's exact author source77f8d688,17 runtime versions,Torch2.10.0+cpu/
TorchVision0.25.0+cpu,CPU4threads,FP32,highest float32 matmul precision and
seed278. Same two official components must match the now-established hashes:
RoMac7a45c80d41ad788a63c641d1b686d7cb3f297f40097c6f4e75039889e5cc8ba,
DINOv2d5383ea8f4877b2472eb973e0fd72d557c7da5d3611bd527ceeb1d7162cbf428.
No cache/weights survived0278;download again only from the same official URLs.
MIT/Apache/runtime notices remain distinct;no paid/gated/NC/model substitution.

## Prospective exact-state proof

First test streaming fingerprints on tiny deterministic arrays:ordering/layout
invariance,one-ULP mutation sensitivity,dtype/shape distinction,scalar handling
and object rejection. Use at most1MiB data chunks,not a full copied state blob.
On a tiny Torch mmap checkpoint verify strict model copy has distinct storage,
exact equal fingerprints,checkpoint weakrefs die after del/gc,and one inference
leaves model fingerprint unchanged. Reset Torch seed278 before constructing the
full model so the test cannot perturb its initialization path.

Then repeat both complete strict finite/key/shape/dtype/loaded-byte checks for
the actual wrapper and descriptor. Assert nonempty tensors do not alias source
checkpoint storage. Fingerprint both full model components,release checkpoint
dictionaries,force ordinary GC and require all checkpoint-tensor weakrefs dead.
Record **current** working set before/after separately from historical peak;
do not claim a reduction until measured. Require model fingerprints unchanged
immediately after release and after the one unchanged neural forward. No
quantization,weight modification,offload/tiling/compilation or changed batching.

## Unchanged physical test and budgets

Every scientific input,role and gate is inherited verbatim from0278:the exact
archived supplied-scan diagnostic pos/neg images,5000material-ID0230 fixture,
1343common-visible points,source-only input rights,network denial,knownK and
single true-baseline gauge disclosure,even training/untouched odd scoring,
.05confidence,2px/.6support/1deg/512/seed278 existing pose solver,3px camera/
2mm **point** capacity and3px composed pose. No original video or medicalSTL,
case002,head fitting or training/upload. This is not an actual-video/surface/head
claim. AST checks must prove evaluate/project/bilinear/pixel_controls unchanged
from scientific source7780d5d;the model.match call/default config also stay fixed.

Same default560/864 symmetric pair and8GiB peak-working-set limit. Implementation
<=600s,asset/runtime install<=300s,exact-state control/full load<=180s,one complete
forward<=180s,physical score<=120s;all closeout within2400s. No neural rerun after
any scientific/resource failure. If the interface itself fails before inference,
record a narrowly scoped ordinary repair without changing this contract.

On failure preserve compact reports/notices/hashes/source refs,no extra source
images (0274 already retains two),remove all exclusive code/model/framework/
cache/env/output,verify protected originals/shared tests and commit local cleanup
before a different route. Retain successful generic fingerprint/grid regressions
only. No production default changed;do not promote conformance into ACCEPT.

## Engineering export exception,registered before any physical score

First source d4e33e2 strictly loads both components and verifies weakref release
and unchanged model fingerprints. Current working set falls3710214144->2047188992
bytes (1663025152bytes measured). One model.match call returns,but the inherited
shape assertion stops before saving any prediction or physical score. The pinned
publisher's batched=True path returns(1,H,2W,4)/(1,H,2W),whereas the inherited
exporter expected(H,2W,4)/(H,2W). No scientific precision failure is observed.
The process is terminal;there is no surviving tensor to export without replay.

Register **one** ordinary engineering replay,within the same original2400s and
8GiB/180s forward limits:drop only the known singleton batch axis after saving
the immutable raw tensors and returned shapes/time/peak. The index view changes
no value,model call,input,seed,dtype,resolution or scientific score. Require final
measured peak<=8GiB,not merely absence of a polling abort. Add an exact checkpoint-
fingerprint versus loaded-model comparison before releasing dictionaries.

This is an explicit deviation from the original single-forward count;preserve
that protocol failure rather than silently calling the original attempt passed.
Original source/log/failure/control remain separately archived. No score or
validation residual existed when authorizing this representation-only repair;
no further replay,scientific parameter change or budget reset follows failure.
Replay capacity facts,if any,are reported separately from whole-protocol status.

## Actual result:memory control passes,physical capacityREJECT

Installer1272d01 completes in151.985s with the exact0278official model hashes.
Scientific first sourced4e33e2;export replay6a8a148. Tiny mmap-copy/weakref and
bounded fingerprint tests pass. Both complete actual component states match
their checkpoint values/storage checks;the replay additionally compares full
checkpoint-value fingerprints to model fingerprints before release. Model
fingerprints remain unchanged after release and after the exported forward.

The first load measures current working set3710214144->2047188992bytes;
replay3700281344->2037256192bytes. Both measured reductions are1663025152bytes.
Historical peak is reported separately and is not claimed to fall. The replay
completes one full default forward in57.422s;whole process peak7267807232bytes
(about6.77GiB) is below the unchanged8GiB cap. Source-grid error0px,raw batched
and unbatched export shapes/dtypes/value-byte hashes match exactly after index0.
This isTECHNICAL_CHECK_PASSED resource/state/representation evidence only.

One independent scorer consumes only saved predictions. Both true-camera/
triangulation evaluator controls pass. Every1343true-common point is counted,
including low-confidence outputs;none is removed by its error.

| Direction | Source-visible | Training | Untouched odd held | All-common correspondence p95 | Common confidence>=.05 |
|---|---:|---:|---:|---:|---:|
|+30->-30|2223|239|650|126.059798px|250/1343|
|-30->+30|2205|246|650|135.649944px|274/1343|

First pose fails ambiguous/insufficient positive-depth support;reverse pose
fails convergence or positive-depth check. No complete camera/triangulated
candidate exists,so camera-p95/point-mm/surface-mm/head errors remainUNVERIFIED.
The pixel numbers are **correspondence** errors on this diagnostic source pair,
not reconstructed-head millimeters or actual-video error. Do not compare them
as a matched-cohort improvement percentage against0274's front->30pairs.
Stop this configuration;no threshold,confidence,precision,resolution/crop/texture
or checkpoint rescue. Original one-forward protocol remainsREJECT due the
explicitly recorded extra interface replay,not quietly relabeled a whole pass.

## Read-only failure checks and applicability boundary

Trace original producer88f00f3:VIEWS maps pos->yaw+30 andneg->yaw-30. Thus no
sign/filename swap is inferred from the score. Independent center/edge and
source-grid controls and raw/export exact-byte checks also pass. A deterministic
every67th-common-ID overlay was actually viewed;source material locations and
predictions disagree substantially. It is labeled SUPPLIED-SCAN INPUTS / NOT
A RECONSTRUCTED HEAD,not a recovered identity or a medical quality image.

The source input is a small unlit gray/noise head silhouette on black,without
natural facial albedo/shading. This is a serious representativeness limitation
for a foundation-image matcher,not proof of the sole failure cause. Known3D
truth validates the arithmetic and this conditional capacity test;it does not
make the rendered appearance representative of the authorized video. Do not
generalize failure to all natural-video methods,or keep rerunning this proxy
with different paint/crops. Future route selection needs evidence tied to the
actual video's observation/rigidity problem,not another surrogate-only promise.

## Closeout scope

Keep compact reports,source refs,complete fixed-cohort queried predictions,
notices/hash references and one labeled diagnostic image. Do not retain full
raw dense tensors,duplicate inputimages,checkpoint/framework/environment/cache
or exclusive failed runners. Retain the successful generic streaming-state and
grid regressions. Actual verified deletion/test/commit details follow below.

## Verified cleanup

Private evidence:assets/private/closed-experiments/0279-roma-lifetime/evidence.zip,
37members,328989bytes,one explicitly labeled diagnostic image,SHA256
d2b714062cea4257d207e12836461fc382ea5c9063f4cd7ac5715d0c331710bd.
CRC/all member SHA verified after deletion. Source recovery7265dbf includes
the exclusive installer/worker;originald4e33e2 and export replay6a8a148 remain
distinguished. Queried fixed-cohort observations/reports survive,not dense maps,
weights or environments. Source images stay in unchanged0274. Binary recovery
requires official downloads and regeneration,not restoring this compact ZIP.

After terminal-worker/exact-path/reparse/archive/caller checks,remove33359data/
cache/bytecode files totaling2808812907logical bytes,and two tracked source files
totaling24729bytes via apply_patch. Combined33361files/2808837636logical bytes;
not independently measured free-disk gain. Successful generic exact-state/grid
math and regressions remain;main environment has noTorch and no live failed
model imports. Production source/defaults match2b817d1. Five protected original/
authorization/fixture/unrelated-file hashes are unchanged,including0207.

Post-removal137shared tests pass in6.071s. Pre-final-commit phase2277.347s is
within original2400s;the single-forward-count deviation still remainsREJECT.
Focused local cleanup commit follows. No push,patient head,medical surface
error or visual acceptance claim. Goal stays active;no additional resource/
proxy/parameter rescue of this fixed configuration is performed.
