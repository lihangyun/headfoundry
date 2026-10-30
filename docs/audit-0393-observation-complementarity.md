# 0393 archived observation complementarity admission

2026-10-30, after0392closeout1dd96a0. Budget10minutes, read-only archive audit.
Hypothesis: texture observations0385and anatomical observations0304 may add
different spatial constraints on their three shared native frames240/300/630.
This is not a repeat of either camera fit or authorization to merge biased
coordinates. Inspect exact archive identities, coordinate convention, populations
and spatial coverage. No raw model forward, optimization, outlier removal,
threshold tuning, medical data, case002, upload or training.
Retain both observation classes and provenance separately. Same-pixel or nearby
coordinates are NOT certified identical material points. Source-frame overlap
also makes their errors potentially correlated. Do not call union size or convex
hull area physical accuracy. If complementary face-region support cannot be
established, do not launch a merged solver merely to increase point count.
Record concrete next admission requirements, not a head-quality claim.

## Actual fixed archive inspection

CRC-compatible NPZ inputs loaded without pickle; archive identities independently
hashed and match historical records:

-0304 `b4098c99c478dc223c3d489dddb662dce61f4003712585fbf111355d07385a52`
-0385 `7e5bc84d7e3cff0c5fab9078e8c61e6632b923bdc0d46d30c6a3b0f1822af1ec`

0304 frozen-xy.npz has xy[4,28,2],frames[0,240,300,630] and28namedIDs;
0385 observations.npz has xy[3,37,2],train28/held9 with sourceIDs. Select only
the three shared frames for descriptive coverage, not a new fit or split.
Both historical adapters use native integer-center720x1280coordinates; these
are archived predictions, not new physical point annotations.0304prepared.json
records original video hash96fb14b83bc35be92bb9a92a90db38f524778c9a2fec930997c37105b8ade892
and exact shared frame hashes. No independent noise model is established.

| Frame | Semantic points outside texture hull | Texture hull area(px squared) | Union / texture area |
| --- | ---: | ---: | ---: |
|240|1/28|41760.0000|1.0251284|
|300|2/28|34405.4359|1.0181476|
|630|1/28|36326.6899|1.0116582|

Native source semantic bounds[xmin,ymin,xmax,ymax] are
[282.3191,619.9672,487.1256,735.4081], versus texture
[280,512,496,752]. Nose/canthi semantic support does not add lip/chin/bilateral
profile measurements; this anatomical limitation follows the frozen0304ID
selection, not from interpreting a convex hull as a visibility mask.

Reproducible read-only calculation: load0304`frozen-xy.npz`xy[1:] and0385
`observations.npz`xy; for each aligned frame, use scipy.spatial.ConvexHull(t).volume
and ConvexHull(np.vstack([s,t])).volume (2Darea), plus
(Delaunay(t).find_simplex(s)<0).sum(). Keep all28semantic/37texture rows,
including historical held rows only for descriptive coverage; no coordinate
values enter a new optimization and historical held evaluations are unchanged.

Decision: do not admit naive pooled fitting as a coverage-improvement route.
The1.17-2.51%hull expansion does not prove the semantic observations contain zero
independent depth information, but there is no evidence here that they cure the
known missing regional coverage or correlated correspondence errors. No new
arbitrary area threshold is imposed. Further combination needs independent
physical localization evidence and explicit region/visibility support, not a
larger point count or averaged coordinates.0392's interpolation explanation
does not cure these defects. No actual camera/head/medical improvement measured.

No runner, image, model, environment or loose output was created; retained
existing archives are the evidence, no duplicate private material required.
No source/default/test changes; the previous170-test result is not represented
as a new execution.0207remains untouched. Goal remains active, notACCEPT.
