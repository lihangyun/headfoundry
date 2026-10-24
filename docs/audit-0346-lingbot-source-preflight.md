# 0346: LingBot-Map source and coordinate preflight

Registered 2026-10-24T00:39:37Z, before local acquisition or execution.
Goal active; account short/weekly usage 10%/2%. Previous turn was a product
limit check, not a live scientific job. Base d9cc9d1; unrelated0207 untouched.

Single candidate: Robbyant LingBot-Map, source
b9dd1b1de535e6d36e777fb42b8433c781bfd783 and lingbot-map.pt only.
Distinct evidence: temporal context predicts camera/depth directly; not the
retired ALIKED correspondence entrance or fixed-room illumination calibration.
This does not establish correct skin motion or head reconstruction precision.

Budget: 40 minutes including documentation/commit; source-only HTTP collection
at most120s and2MiB total. No checkpoint, dependency install, source import,
inference, patient data or scan access. Stop on rights conflict, identity
mismatch or budget; an unavailable endpoint is UNVERIFIED, not model REJECT.
Only public pinned code/license/model metadata are acquired. No threshold,
checkpoint, precision or frame sweep. Model quality remains UNVERIFIED.

Required evidence: explicit model and code grant, published checkpoint
identity, minimal inference dependencies/hidden downloads, safe strict loading,
camera direction and image resize/crop transforms. Review source before
designing a separately registered runtime/physical validation. Do not promote
source checks into camera3px, medical2mm or visual acceptance.

Read-only web findings preceding registration: upstream model card explicitly
states Apache2; source LICENSE.txt is Apache2. Public checkpoint page publishes
SHA256 ee665103348e07e6b826d529b8e61de8f413d5432a4f2e84970d6c8fd2e1cd72.
Local bytes have not been acquired or verified. GCTStream defaults tracking off;
camera decoder outputs C2W, two FoVs and fixed centered principal point.
Crop loader rounds resized height to a patch multiple. Default demo loading
must not be copied without strict state matching and safe deserialization.

Primary sources:
- https://github.com/Robbyant/lingbot-map/tree/b9dd1b1de535e6d36e777fb42b8433c781bfd783
- https://huggingface.co/robbyant/lingbot-map/blob/main/README.md
- https://huggingface.co/robbyant/lingbot-map/blob/main/lingbot-map.pt

Ponytail: reuse existing geometry/runtime tools; no new framework abstraction.

## Executed source evidence

Public-text collector completed in5.859s.13files/197226bytes retained under
assets/private/lingbot-source-0346, indexed by receipt.json with URL and SHA256.
Second invocation pinned the model card to HF revision
204754b72bb24f561f8d7e7e1e4e4cd9e809adf9 and checked its Git blob identity
985cb20e109a39ab2481b854d2740c11d0a146d4. An additional offline replay checked
every retained SHA256/size. Model metadata confirms lingbot-map.pt size
4632303465bytes and the registered SHA256. These are publisher identities;
checkpoint bytes are NOT locally verified. No weights or models executed.

### Adapter requirements established by source inspection

- Model card License section says Apache2 and links the source grant.
  Source license SHA256 c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4.
  Complete transitive import/license review remains pending; top-level grant
  must not be substituted for checking extra runtime dependencies.
- GCTStream selects camera/depth heads, no point head or tracking by default.
  Its SDPA path exists, but imported block/attention modules still need full
  inspection before claiming installation needs no FlashInfer. No Kaolin,
  sky mask, UI or batch-render pipeline is required by the selected entry.
- Aggregator base tries loading the optional DINO path even when empty and
  catches exceptions. A local adapter must explicitly avoid that optional
  load and require complete final state coverage; no silently random weights.
  Stock demo uses weights_only=False and strict=False. Use safe deserialization
  and strict key/shape checks, stop on mismatch; never enable unsafe fallback.
- Camera output is OpenCV-axis C2W [R|t], with t the camera center. For shared
  W2C consumers use R.T and -R.T@t. The two FoVs generate separate fx/fy and
  principal point W/2,H/2; no recovered arbitrary principal point/distortion.
  Preserve pixel-edge versus integer-center conventions explicitly.
- Crop path for720x1280 resizes to518x924, then keeps rows203:721, producing
  518x518. sx=518/720 and sy=924/1280 differ; one scalar scale is incorrect.
  In edge coordinates x'=sx*x,y'=sy*y-203. For integer centers include
  half-pixel offsets. Inverse-transform K as well as observations, and never
  count cropped-out geometry as observed. Pad mode is a different input
  configuration; choose it before scores, not after a failure.

Status: PARTIAL_SUCCESS for source preflight only; runtime/import closure,
checkpoint coverage, GPU capacity, physical camera accuracy and real head
quality remain UNVERIFIED. This is not a failed model route and no failed
model artifacts exist to retire. Keep small evidence and reproducible collector.
No shared code/defaults/inputs or0207changed. Full shared suite was not rerun
for this isolated public-text collector; it would not establish model quality.

Next concrete entry: complete pinned block/attention/backbone/head import
closure; then freeze one inference configuration and owned physical context,
bounded local checkpoint acquisition/strict loading and hardware trial. No
patient pass until coordinate replay and independent camera validation are
defined. Proceed autonomously within existing authorization. Do not spawn
another camera-ambiguity toy audit instead of completing this candidate.

## Source closure follow-up,2026-10-24

Collection completed in16.093s:41text files/604069bytes total. All package Python
files and available license/notice files were checked against the pinned Git
tree blob identities; an AST import inventory is in receipt.json. This is
inert text, not an installed framework. Receipt replay verifies all41hashes.
FlashInfer import is guarded by ImportError; SDPA selection avoids its runtime
cache path. Optional lietorch/distortion imports are also guarded and unused
for direct camera/depth inference. DINO backbone contains no load call;
the optional aggregator load identified above is the remaining load boundary.
No extra checkpoint fetch is needed by the inspected direct entry. Torch,
NumPy,SciPy,einops,typing_extensions,huggingface_hub,tqdm are its external
imports; Pillow/TorchVision are used by the optional image-loading utility.
Their exact installed distribution licenses/versions must accompany runtime.

Coordinate clarification from geometry.py: upstream unprojection uses integer
arange pixel coordinates and principal point W/2,H/2. W/2 alone is NOT proof
of an edge-origin convention. Preserve these numbers in model coordinates;
apply the actual PIL integer-center resize/crop affine when mapping to native
pixels. Do not blindly subtract0.5from the predicted principal point. Earlier
edge-coordinate formula is only a coordinate conversion, not an instruction
to reinterpret the network output.

TECHNICAL_CHECK_PASSED for pinned source acquisition/inventory; model behavior
remains UNVERIFIED. Hardware readout: RTX3070,8192MiB total,6493MiB then free;
this is not a successful capacity test. Source budget stayed below120s/2MiB.
