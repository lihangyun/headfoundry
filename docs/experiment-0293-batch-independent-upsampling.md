# Experiment0293:batch-independent convex upsampling,software audit only

Registered2026-10-21T22:22:40Z,before scored execution;implementation is unrun.0292 is
closed and exclusive integration retired at7c0a4ae. Goal active;account allowed.
No tracker runtime/checkpoint is reinstalled and no human material is read.

Evidence:0292 allocation failed exactly at the9-neighbor broadcast product.
Pinned publisher source e7553135e7b361590dbccd10e2b274b024f41cd6,
nets/alltracker.py SHA42a203dfe1f4f6f035570c0c97a83172bd769591fa5930deda422ddac42f7807,
[upsample_data and both callers](https://github.com/aharley/alltracker/blob/e7553135e7b361590dbccd10e2b274b024f41cd6/nets/alltracker.py)
normalize across9neighbors,unfold zero-padded3x3patches,reduce9,and permute
subpixels. No operation mixes the batch axis. Both flow and visibility logits
use this same operation,including its factor8. Do not silently alter logits.

Single variable:partition only the independent batch axis into fixed chunks1,
preallocate full output and fill every batch item. Preserve FP32,factor8,9-way
softmax/reduction,zero padding,channel/order/subpixel layout. This is a different
allocation algorithm,not a precision/input/allocator/threshold rescue. Static
native product falls from1132462080 to70778880bytes per chunk;this is only an
analytic temporary-size bound,NOT measured GPU peak or network capacity.

Budget900s whole,implementation<=300s,one NumPy audit<=30s,tests<=60s,remainder
documentation/local commit. Audit fixed seed293,N=1/3/16,H=7,W=11,C=2,FP32
contiguous and strided inputs:compare ALL vectorized batch/chunk outputs
bit-for-bit;finite and exact shape. An independently indexed scalar-neighbor
oracle checks all pixels on a fixed small asymmetric two-channel fixture,
max<=1e-5inputpx. Uniform weights/borders and channel/subpixel axis sentinels
must agree with the explicit9-neighbor formula. Malformed shape/dtype,empty
batch,nonfinite inputs fail closed. No sweep/replay if any scored check fails.

Pass means TECHNICAL_CHECK_PASSED for NumPy algebra/index only. CUDA reduction
rounding,full-network pixel equivalence,actual native resource peak and physical
3D tracking are still UNVERIFIED. Further installation/GPU/control execution
requires its own bounded preregistration. Camera3px,skin2mm and head gates stay.
On failure archive compact report/hash/source and clean only exclusive new
runner/output before a different route;successful generic numerical oracle may
remain. No video/scan/case002/training/upload/default changes or head output.

## Actual result:TECHNICAL_CHECK_PASSED for algebra/index only

Executed6916eed,one audit terminal0 in.140s. All394240FP32 batch/chunk values
are bit-for-bit equal across the six fixed contiguous/strided controls. Two
independently indexed fixtures each score all1536values;asymmetric max delta
6.33272e-7px,uniform/border1.58946e-7px. Seven invalid inputs are rejected.
The analytical temporary bound is1132462080versus70778880bytes,not measured
CUDA memory.140shared tests pass in5.030s;finished22:23:12Z within900s.
Source checker SHA f98f335363fc654c81a44645935a752f41faa3b4f1120f3cc3bbc8b6b173c359.
Compact audit/test/identity records remain under assets/private/convex-upsampling-0293.
No runtime/checkpoint/medical input is installed/read. Actual GPU/software-network
equivalence and physical precision remainUNVERIFIED;no camera/head is generated.
