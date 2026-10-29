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
