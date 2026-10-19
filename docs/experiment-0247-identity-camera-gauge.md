# Experiment0247: separate coordinate gauge from anatomical identity information

Date:2026-10-19. Pre-registered before new numerical analysis. Status:UNVERIFIED.

0246 regresses scan nose/mouth despite improved fitting contours. A video-only
internal similarity shows a small scale/frame component. Test that hypothesis
without fitting another head or realigning any rejected output to a scan.
Do not assume that imposing seven equalities on the300 identity coefficients
is a harmless coordinate choice:those coefficients can couple rigid/scale
components with useful nonrigid anatomy.

Only exact previously cleared FLAME2023 Open,0241 safe video baseline,0246
frozen rejected coefficients and original generic skin-component IDs are read.
No source scan,clinical pilot file,scan-evaluation directory,photo/video decode,
case002,new model,training or upload. Block all STL/pilot/scan-evaluation paths.
Preserve every output/default and fixed scan metric;produce no replacement mesh.

1. On the licensed generic neutral,apply exactly one known similarity:
scale1.006,Rodrigues(.01,-.015,.02),translation(.0003,-.0008,.0002) native.
Compensate proper perspective cameras at yaw0,+/-45,+/-90,distance.65 and
focal937,(360,640). All vertex projections must agree<=1e-8px. This control
demonstrates global shape/camera gauge,not that the learned identity family
contains a free pure similarity or that the real cameras are accurate.
2. Form an orthonormal seven-generator translation/rotation/scale tangent on
the baseline's3931 native skin vertices. Split the exact identity basis into
similarity and orthogonal-local fields. Use SVD rcond1e-10,not a regularizer
sweep. For the frozen actual0246 coefficient change,solve the single least
squares local-field replay within the coefficient nullspace of the similarity
map. Record rank,local distortion,coefficient bounds and mesh guards without
exporting or scoring its hypothetical geometry. Hard coefficient gauge locking
is eligible for later consideration only if local replay relative error<=1%
and original beta bounds/safety pass. Otherwise reject the naive hard lock.
3. Independently test a full-family **coordinate-only** centroid/RMS-radius
normalization and analytic derivatives. It must preserve every pair-distance
ratio and,after exact camera compensation,all projections<=1e-8px. Check10
seeded native directional derivatives and small complete unit derivatives.
This removes translation/uniform scale only,not anatomical shape or rotation;
it is not a reconstruction improvement or a calibrated millimeter scale.

Budgets:one60s numerical run,no pixel/scan fitting or parameter search. Never
apply a post-hoc transformation to0246's OBJ,images or scan statistics. Passing
coordinate mathematics adds no image information and cannot fix missing
posterior evidence,invalid held views or physical camera identifiability.
Choose the next real experiment from these actual results,not from a prettier
registration score. Commit only code/tests/non-identifying findings.

## Actual result and decision

The3.11s run passes exact-camera equivalence at<=3.42e-13px and native
normalization directional derivatives at6.13e-12. The skin-field similarity
map has rank7 and293-D coefficient nullspace.41.742% of total squared native
identity-basis energy projects onto the seven-generator tangent;this is basis
coupling,not a fraction of reconstructable anatomy or a new accuracy metric.

The single gauge-null local-field replay of0246's frozen change loses11.411%
relative local displacement,exceeding1%. Its coefficients remain within3,but
the hypothetical native geometry has4 normal reversals,min area ratio.1621.
Reject the naive seven-equality latent lock;do not install it into a head fit.
No hypothetical mesh is exported/rendered/scored.198 tests pass.

Centroid/RMS coordinate normalization preserves full-family shape up to uniform
similarity and exact camera compensation,but adds **zero independent image
information**. It is not a demonstrated fix for0246's3D regression. All old
OBJ/images/fixed scan metrics remain unchanged. No new accepted head/camera,
partial product success or source-driven realignment follows.

After excluding this blind hard-lock fix,refresh current free-commercial
geometric initialization candidates using official model/code license evidence.
Only a different licensed observation/camera mechanism merits another bounded
known-geometry screen;do not spend another real head fit on coordinate cosmetics.
