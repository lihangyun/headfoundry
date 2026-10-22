# Experiment0318:does a genuinely new motion axis add focal information?

Registered2026-10-22T16:07UTC after0316/0317closeout4fec116,before computation.
Whole900s to16:22UTC;worker120s/1GiB,CPU4math threads. No reconstruction output
or physical camera fit. Previous turn is progress:failed focal-prior candidate
was rejected/retired and fixed-band source census supplied bounded new evidence.

0311established local sigma(logf)=.0760183for141procedural tracks/.5pxnoise.
0316rules out treating one learned Kguess as precise;0317did not admit scene
orthogonality. A different information source remains possible:additional
cross-axis observations. Actual video has qualitative pitch,but no measured
20degree pose or certified correspondences is assumed. Do not request footage
or restore failed trackers/0308cached solve to test this hypothesis.

Single variable:geometry of ONE added view,with identical number/identity of
new observations. Compare repeat-anchor camera versus camera pitched+20deg
around the existing procedural cloud centroid. Both retain all five original
poses/K/141points/clean training rows/anchor2/baseline3 unchanged. New141rows
project those same points with fixedK;new camera extrinsics remain six FREE
nuisance variables in both information calculations. Pivot describes only
synthetic input generation,not a fixed-pivot human-motion assumption or prior
supplied to an estimator. No new point/seed/noise/focal/iteration sweep.

Read only the successful0311raw linearization capsule,check its SHA/CRC and
replay baseline sigma. Reuse unchanged shared linearize/focal_information.
Profile local logf against all free camera/point nuisance columns at exact truth,
same rcond1e-12 and declared .5pxindependent Gaussian coordinate noise. No random
noise draw,solver fit,estimated step or held observation is used. Preserve all
Jacobians/ranks/singular values. Require proper camera,positive depth and all
new points inside native image;outside data stops rather than pruning points.
Half-step/forward checks stay inherited. Verify that appended-view parameter
columns preserve every original residual/Jacobian block and that duplicating
an entire Jacobian gives the analytic1/sqrt(2)noise-information scaling.

Decision:only if pitch is locally identifiable,sigma(logf)<.02ANDlower than the
same-size repeat control does it justify a separately bounded noisy camera
capacity test. Otherwise no solver/new-model trial is justified by this cue.
This local regular-unbiased/Gaussian sensitivity is NOT achieved precision,
95%coverage,global identifiability or patient feasibility. Existing0255/0256
silhouette-only family remains frozen;this is not a silhouette loss variant.
Even a positive result admits no actual-video pose/3px/2mm/head/visual quality.

No private human pixel/scan/case002content,download,training,upload,new package,
source/default or gate change. Archive small read-only evidence/Git source and
retire one-off driver after tests/protected hashes. No model stack to keep.
