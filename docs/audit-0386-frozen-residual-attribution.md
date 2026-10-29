# 0386: frozen residual attribution, no reconstruction replay

2026-10-29. After0385closeout e2f2875, inspect only archived0383/0385evidence.
Budget15minutes starting14:18UTC. No weights, new frames, camera optimization,
point correction/removal, split change, scan/case002 read or training.
Keep0385REJECT and all3px/2mm/visual gates. One diagnostic computation only.

Question: is the worst held error accompanied by weak matcher consistency,
which fixed camera pairs disagree, and does the small admitted population even
cover the lower face? Competing explanations remain wrong correspondence,
nonrigidity, camera-model bias and triangulation error amplification.

Freeze all37admitted points and the original9held. Compute camera-induced
fundamental matrices (not data-fitted F) for allthreepairs, symmetric line
distances and Sampson residuals, plus archived confidence/FB evidence and
coordinate ranges for allpoints. Check exact synthetic projections give zero
epipolar residual; adding a perpendicular image displacement must fail that
check. Numerical tests prove arithmetic only. Do not infer pixel or mm truth
from Sampson error. No new numerical acceptance threshold or reranking intake.

Visual review uses the unmodified stored tracks.png sheet already inspected.
Sourcequery38=(448,608) appears near the upper eye region, but an overlay and
human visual impression do not certify a persistent material point. Eye gaze
differs visibly across these frames. This is a hypothesis cue, not proof that
eye motion explains the measured residual. Record observations separately.

Keep compact JSON/source evidence, source recovery and close the exclusive
diagnostic runner. If evidence cannot distinguish causes, say unresolved rather
than removing the point or claiming successful camera/head reconstruction.

## Executed evidence and interpretation

One arithmetic run completed in0.337s. Exact synthetic epipolar residual check
and perpendicular5px perturbation check passed. No F estimation or camera solve.

| Frozen camera pair | Training Sampson p95 px | Held Sampson p95 px |
| --- | ---: | ---: |
| 0-1 | 0.595591 | 0.634703 |
| 0-2 | 0.353669 | 0.371692 |
| 1-2 | 1.139480 | 1.381605 |

Forquery38, forward/backward confidence is0.652395/0.816960 and
0.263714/0.672742; FB=.424470/.513048px. It comfortably passed the original
.05/.75 screening, so its failure is not a near-threshold numerical accident.
It does not prove that stronger confidence screening would fix correctness.
Its fixed-camera Sampson errors are.795356/.274367/1.646138px for01/02/12;
target line distances1.136311/.381157/2.266718px, whereas0385third-view
prediction error reaches4.821992px. Two-view epipolar proximity does not enforce
one consistent triangulated point across three views; replacing3Dprediction
with a smaller epipolar metric would hide this failure, not solve it.

Pair12has greater residual than source pairs in both training AND held sets.
Thus the evidence is not simply "one held observation must be wrong". These
are residuals under a fitted model, not independent true-camera measurements;
they cannot uniquely attribute error to a particular view or prove nonrigidity.
The matcher supplied only source-rooted01/02 observations, not an independent
12measurement. A useful future consistency witness must add genuinely new
image evidence, not derive another check from the same two root predictions.

All37admitted source coordinates lie withinx280..496,y512..752. On the stored
native image this covers forehead/eye/midface and ends above the lower lip/chin;
it does not establish chin/jaw/bilateral/fullhead coverage. Even ifquery38were
fixed, this is not enough evidence for the requested complete reconstruction.
No anatomical segmentation groundtruth or physical identities were created.

Decision: preserve0385REJECT; do not pruneeye38, replace the quality metric,
or install a new model. Local image evidence and time-continuous observations
are candidate independent witnesses, but their errors and occlusions must be
measured before using them as extra constraints. Do not assume a temporal chain
is correct merely because it closes. No follow-on method was run in this audit.

Evidence archive:assets/private/closed-experiments/0386-frozen-residual/evidence.zip,
11607bytes,2members, SHA3bb4d0f49f7467c7984a1503dd55baebabb25e78f73d69502ea7da91dce090bd.
Contains all37per-point residuals/confidence/FB/coordinates, controls and source.
Original archives are read-only and retained; no loose image/mesh/model output.
Audit statusTECHNICAL_CHECK_PASSED means arithmetic only. Reconstruction remains
REJECT/UNVERIFIED, with no new mesh or medical accuracy gain.

Closeout:source recovery5ec190b. All9protected hashes and both prior archives
unchanged;0386CRC/hash/source equality verified before removing the one exclusive
runner. No generated loose files, weights, environments or original data deleted.
167shared tests passed8.179s; no outside caller of the diagnostic runner.
Only the compact archive and report remain. No production-default modification.
