# Audit0287:one new direct-query correspondence candidate,preflight only

Registered2026-10-21T13:49:39Z before pinned source/model/dependency inspection.
0286 is closed/cleaned at25e619c. Budget900s including records/local commit;
metadata/source inspection<=300s. No checkpoint/environment install,inference,
camera/head fit,private video decode,scan/case002 read,training or upload.

0286's adjacent-pair advantage does not causally prove accumulated drift,but
justifies checking a genuinely different observation mechanism. The candidate
AllTracker estimates query-to-many-frame dense flows rather than simply chaining
adjacent DIS fields. This mechanism may avoid one source of accumulation;it
does not guarantee material identities,rigidity,occlusion or3px/2mm quality.
No CoTracker/oldTAPNext/RoMa/DA3/MapAnything integration is restored.

Inspect only official aharley/alltracker GitHub/HuggingFace and its paper.
Lock actual source/model revisions,checkpoint identity/size,code/weight license,
runtime dependencies and default evaluation/window/normalization path. Record
uncertainty,especially CPU/full-video resources and external pretrained assets.
Fail closed on rights gaps. No inference or download trial during this audit.
Third-party general benchmarks cannot be transferred to the patient's face.

The main prospective change would be direct-query temporal correspondence,
not another global-camera optimizer or a filtered subset of0267tracks. Any
subsequent installation/control/actual-video trial requires its own prospective
fixed inputs/capacity/budgets/stop contract and independent held evidence;this
document does not authorize silent preprocessing/precision/threshold sweeps.
No actual reconstruction acceptance or production/default change follows.

## Result:permissive candidate,execution still UNVERIFIED

Official source revisione7553135e7b361590dbccd10e2b274b024f41cd6;model revision
c8ba31225828cab9ec512d0627f0f826e641a877. Source[MIT notice](https://github.com/aharley/alltracker/blob/e7553135e7b361590dbccd10e2b274b024f41cd6/LICENSE)
and publisher[weight card](https://huggingface.co/aharley/alltracker) independently
declare MIT. Retain attribution;this is not a blanket training-data/privacy/
patent or dependency clearance. Only default full alltracker.pth is a prospective
candidate:66005722bytes,LFS SHA256
ffd9ebcfb6d206d594b646999a150540f92c049cf9b2bf940facf7123f62aa1d.
This is publisher metadata,NOT downloaded-byte verification. Tiny/Kubric-only
alternatives were inventoried,not selected or downloaded. Exact card-text SHA
f0ea38ffeb94f94c853029a28b9f59f05cc447a2a646f5c4ea0a4e90b1653d0f.

The[paper](https://arxiv.org/abs/2506.07310v2) describes16Mparameters,query-to-many
correspondence and high-resolution results on a40GB GPU,not patient precision.
Sliding source retains the original query feature,but seeds later windows from
prior flow estimates:NOT completely history-independent or drift-free.

### Source integration hazards found before installation

- Core imports Torch,torchvision.ops,einops,NumPy and local basic/misc. Actual
  compatible binary versions/licenses remain to be locked;do not blindly install
  the much larger training/demo requirements set.
- Net defaults init_weights=True;ConvNeXt then fetches another torchvision
  pretrained asset before loading AllTracker. A future loader must instantiate
  init_weights=False and prove strict complete released-state coverage,not leave
  random/missing parameters. Public hub/demo also use mutable main URLs.
- get_fmaps has two unconditional .cuda() calls. The demo assumes cuda:0 and
  defaults to shrinking/truncating at maximum dimension1024/400frames. Running
  as-is would silently violate a full native-input contract;it was not executed.
- RGB float0..255 is internally normalized by ImageNet mean/std;output is relative
  XY flow. Native-pixel conversion,padding and border checks remain necessary.
  Confidence is not certified physical identity/visibility.

Fixed-revision source SHA256(no persistent framework copy):

| File | SHA256 |
| --- | --- |
| LICENSE | ab740abe5c34e17963fe4d6a1f68a3dcd35bbc05dc520cf08d7a062c0ea13c79 |
| nets/alltracker.py | 42a203dfe1f4f6f035570c0c97a83172bd769591fa5930deda422ddac42f7807 |
| nets/blocks.py | 0c347f79b53367e0a99fb8d5bbe65346def904940f07dd361349af1da4eb0672 |
| utils/misc.py | 4ac64b714891789b21f1776292c7b9bd580031950f8df4398c9718922e7dbe90 |
| utils/basic.py | 8a9057ef6ddecdc202ba49693dabede6c63dde204b15ec43b4bb81dfaed910a9 |
| hubconf.py | 58b21de66f17f292e751028119083903a24a08491555b224777f907207a7613f |
| demo.py | dcbe752c86fcf50afd5ac6daae629141ee1a4ba0f97edf65fd7257479d535e9b |

### Resource evidence,not model inference

WMI's AdapterRAM is not trusted;nvidia-smi exits255 with Failed to initialize
NVML:Unknown Error. Read-only nvcuda.dll calls instead return cuInit=0,count1,
RTX3070,total8589410304bytes,compute capability8.6,driver API13030. No context,
allocation,kernel or Torch runtime was tested. Physical RAM34269908992bytes;
free GPU memory UNKNOWN. NVML failure is not CUDA failure;no driver changes.

CorrBlock stores five all-pairs target feature-correlation levels. B=1,window16,
FP32,stride8 gives16*4*N0*sum(N_level) bytes;target dimensions halve/floor:

| Input HxW | Correlation-pyramid bytes | GiB(correlation only) |
| --- | ---: | ---: |
| Native1280x720 | 17648640000 | 16.4366 |
| Demo-scale1024x576 | 7238320128 | 6.7412 |
| Illustrative512x288 | 451805184 | .4208 |

These exclude features,activations,temporary products,input/output copies and
allocator overhead;NOT measured peak memory or a512-input trial. Native default
window cannot fit in this8GB VRAM just because its checkpoint is66MB. Future
fixed-capacity/input schedules need separate native-pixel/resource controls;
no silent downscale/window/precision rescue or CPU feasibility claim.

CoTracker's[official license](https://github.com/facebookresearch/co-tracker/blob/main/LICENSE.md)
is CC-BY-NC4.0 and remains excluded. No checkpoint/environment/framework installed,
no private material read or uploaded. Inspection ended13:52:36Z,177s within300s;
whole900s phase includes documentation/commit. PreflightTECHNICAL_CHECK_PASSED
for source/publisher-license/resource accounting only;actual execution,
correspondence,camera,medical/head and visual quality allUNVERIFIED. Next register
a bounded complete-state/resource control,not a promise this will solve a head.
