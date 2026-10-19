# Experiment0246: unaccepted shared-head correction from valid profile evidence

Date:2026-10-19. Pre-registered before any head correction. Status:UNVERIFIED.

0245's four-view prerequisite fails uncertain source347. Do not un-reject or
rerun that configuration. This is a separately declared unaccepted experimental
geometry diagnostic under the already authorized lane,not a new acceptance
standard or a production path. Keep required347 validation `REJECT` throughout,
even if other numbers improve. The full complete-head goal is unchanged.

Use only the two reviewed213-row fitting profiles139/416 and the already frozen
detector-free poses from0245-domain-replay. Shape-held69 has a separately fixed
baseline-only training-row pose and valid observation; keep it fixed. Do not
refit poses,choose another view,trim any row,or use uncertain347 as a fitting
constraint. Persist its original uncertainty failure alongside this candidate.
No new model,detection,training,scan-derived input,ROI or hyperparameter search.

One head correction uses exactly0245's declared finite-domain objective,bounds,
frontal2px self-protection and original mesh guards. Reuse its checked solver
with only3 prepared views available,not an invented fourth pose/trace. All213
rows per available view remain scored,including adjacent held rows. Original
347 is **missing required validation**,not counted as passed or zero error.
Pose/shape fit180s,one configuration,max5 constraint-generation rounds,
SLSQP120 iterations/ftol1e-8 per round. Treat out-of-row-domain **trial** costs
as+infinity to backtrack,as independently checked in0245;never accept missing
rows or alter the finite-domain objective. Add no new numerical rescue after
this attempt. Export only safe experimental NOT-ACCEPTED geometry.

Independent evaluation after inference must freeze0241's same evaluation4x4
for both baseline/candidate,unchanged0237 sample masks and both full distance
directions. No ICP,new similarity,mask trimming or source feedback. Actual
front/bilateral/oblique/back white comparisons and exact source-photo overlays
must distinguish shape changes from metric changes. Require regional absolute
2mm targets and all original image/topology/visual gates for actual acceptance;
any facial gain here is bounded diagnosis only.347 failure,native62 boundaries,
unobserved cap/posterior and physical camera uncertainty cannot be waived.

## Actual result: source error regression,REJECT

One51.15s correction completes two predeclared constraint-generation rounds
(4 then5 video-derived active faces,61/65 iterations). Final full-mesh local
guards pass:0 normal reversals,area ratios.209188..2.944709,frontal self-drift
2.000000000264px (numerical tolerance1e-7). Native62 boundaries remain;this is
not a collision/watertightness or physical-camera certificate.

| Available exact view | Baseline held-row p95 px | Candidate held-row p95 px | Final first-hit visible rows |
| --- | ---: | ---: | ---: |
| 139 fitting view | 5.341 | 1.230 | 213/213 |
| 416 fitting view | 6.416 | 1.680 | 212/213 |
| 69 shape-held,baseline-conditioned pose | 5.385 | 6.275 | 213/213 |

All213 rows per view remain scored.416 row712.5 loses exact first-hit support,
native gap.0015313 (about1.53mm nominal units);it is not deleted or called
visible.347's original source measurement is still explicitly REJECT. Head
acceptance,overall image validation and conditional profile gate remain REJECT.
An extra unit test enforces that three available-view technical passes cannot
erase a required missing-view failure.

Separate evaluation reuses0241's **exact same**4x4 with no realignment;
baseline distance p95s replay bit-exactly(0mm discrepancy). Fixed odd source
facial samples,1024 each,show:

| Original region | Baseline p95 mm | New candidate p95 mm |
| --- | ---: | ---: |
| Nose | 4.591 | 5.100 |
| Perioral | 2.391 | 3.067 |
| Chin | 3.492 | 3.395 |
| Left-image cheek | 3.526 | 3.797 |
| Right-image cheek | 3.479 | 3.533 |
| Forehead | 3.467 | 3.403 |
| Other frontal face | 4.101 | 4.669 |

Nose/mouth regress;small chin/forehead changes do not justify promotion. No2mm
regional target is reached. Full source p95(including unscoped source defects)
27.865→27.997mm,whole-output reverse56.672→58.064mm also fail. Source and
acquisition uncertainty remain unchanged. Lower2D fitting error demonstrably
does **not** establish improved3D geometry in this configuration. Stop it;no
focal/ridge/bounds/row-subset rescue or further fitting follows these metrics.

Actual18 source/baseline/candidate canonical white images and6 video overlays
were inspected. Same video-camera pose is used for both shapes in each overlay,
so a camera change is not disguised as a shape change. Source facial contour,
ears/skull/neck and eye-state differences remain. No clear whole-head likeness
gain or visual acceptance is asserted. One common image-only crop across all18
raw white images is[165,442,553,989];originals are untouched.

Independent coefficient geometry replay5.56e-17native,OBJ4.996e-13native and
OpenCV selected-envelope projection replay4.55e-13px pass.195 unit tests pass.
These verify numerical/rejection plumbing,not likeness. Private evidence root:
`assets/private/bounded-profile-geometry-0246/`,with experimental NPZ/OBJ,
all failed rows/views,scan-distance arrays,actual PNGs,all process outputs and
test/replay capsules. No private patient asset is committed. Defaults/case002
stay unchanged;the old video head is not replaced by this rejected candidate.

## Read-only discrimination after rejection,no additional candidate

Using all11731 skin triangle edges instead of only facing-contour candidates
on this **same frozen mesh/cameras** changes the predicted envelopes by<3.5e-13px
and leaves the same one failed support. Missing open-boundary edge candidates
therefore do not explain this result. No raster tolerance or row was changed.

A separate uniform3931-skin-vertex **video baseline internal** similarity test
(not registration to a scan) finds scale.9939991,rotation.22187deg,translation
norm about.000264 native. Raw all-vertex displacement p95=.002661 native;
after this diagnostic-only internal similarity residual p95=.001913 native.
This indicates a nonzero global size/frame component mixed with local identity
changes. It does not prove that all regression is gauge drift. The matrix is
**not applied** to any OBJ,render or scan metric;no new alignment is selected.

Before another contour fitting trial,test whether anatomical identity changes
can be separated from global similarity/camera distance in a scan-free native
fixture. A declared gauge constraint is a distinct supported hypothesis,not
permission to realign the rejected output or tune current weights. Physical
camera identifiability and valid independent observations remain required.
