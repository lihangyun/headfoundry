# Experiment 0017: locked LighterGlue and whole-track camera validation

Date: 2026-09-07. Status: `REJECT` for the real-photo camera candidate.
No baseline replacement, formal head/texture implementation or visual parity claim.

## Local asset and validation contract

`examples/lighterglue-asset-lock.json` pins the official matcher checkpoint,
upstream revision, reviewed Kornia 0.8.1 implementation and CPU runtime. The
published upstream and Kornia licenses are Apache-2.0; see the source ledger.
The loader checks runtime and byte hashes before strict matcher-state loading.
It constructs only Kornia's deterministic confidence buffer; it does not execute
the extractor bundled with the checkpoint or download fallback weights.
Photo digests and local-only consent are checked before processing.

Matching supplies 69 three-view index cycles. A fixed greedy rule requiring
8 px separation in every view retains 51 tracks. Every fifth retained track
is held out in all three views: 40 training, 11 held-out. This split is frozen
before camera fitting. Closed cycles and spatial separation are not proof of
physical correspondence or comprehensive facial/profile coverage.

## Fixed-calibration camera checks

The primary variable is camera initialization/refinement; intrinsics remain
fixed at a focal length of 1800 px. No head prior or texture fitting is added.

| Pair | Plain held-out Sampson p95, px | Robust training support |
|---|---:|---:|
| Frontal / first intermediate | 2.461261 | 12 / 40 |
| Frontal / second intermediate | 1.988561 | 14 / 40 |
| Intermediate / intermediate | 1.969805 | 16 / 40 |

The plain pair rotations have a 5.120125 degree loop discrepancy. Composing
their poses and fitted translation scales produces 258.280007 px p95 across
all 33 held-out third-view predictions, despite 100% positive depths. Pairwise
Sampson distance is not the multiview reprojection gate.

The separate `robust_refine_pose` entry point samples only training pairs with
seed 0 and 512 trials, then refines the selected training consensus. Its fixed
2 px threshold requires at least 12 pairs and 60% support (24 of 40 here).
All three real pairs fail support; the thresholds are not relaxed after seeing
validation. Reports preserve candidate counts and full-candidate errors, not
just small selected-point errors.

## One prior-free joint fit

Starting from the frozen plain cameras, one sparse bundle adjustment jointly
fits only the 40 training points and two camera poses. The frontal camera and
intrinsics stay fixed; a baseline norm constraint fixes scale, with an exact
final gauge normalization. There is no frontal shape/depth prior. The fixed
budget is 300 function evaluations, soft-L1 residuals with 2 px scaling.

The solve converges after 222 evaluations. Training reprojection p95 is
3.520147 px. After optimization ends, each of the 11 untouched tracks is
triangulated from two views and predicted in the third, cycling all three
targets without fitting those points back to the cameras:

- All 33 predictions: median 2.735186 px, p95 7.545592 px, maximum 8.157424 px.
- Training and held-out positive-depth fractions: 100%.
- Decision: `REJECT`; the 3 px multiview gate remains unchanged.

The complete 33 residuals, frozen split, camera matrices and source/script
hashes are retained in immutable private reports and independently read back.
The 33 residuals are correlated checks of 11 tracks, not 33 independent subjects.
These results cannot be compared directly with earlier detector-landmark
populations or used to claim improved side-profile reconstruction.

## Engineering safeguards and next gate

Synthetic 10%/20% wrong-match cases exercise deterministic consensus and unseen
points. A noisy pure-rotation case previously returned positive-depth unit-
baseline geometry; the new default rejects median triangulation angles below
1 degree and reports the positive-depth training angle distribution. Exact
duplicate endpoints and non-upper-triangular intrinsics are also rejected.
These reproducible safeguards are not evidence that those bugs caused the
real-photo failure. Existing camera entry points remain unchanged.

`python -m unittest discover -s tests -v` passes 40 tests, including the new
loader drift check. Tests establish bounded technical behavior, not visual
acceptance. All photos and identity-specific outputs remain local and ignored.

Next candidate: the specifically named, officially Apache-2.0 `DA3-BASE` for
camera initialization, with its own asset lock and independent evaluation.
No DA3 execution or accuracy result is claimed here; Large/Giant models are
not substitutes. Formal geometry and texture remain behind the camera gate.
