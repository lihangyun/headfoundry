# Experiment0253: independent external-motion proxy prerequisite

Date:2026-10-20. Pre-registered before descriptors,matching or geometry scoring.
Status:REJECT at observation-count prerequisite. Previous0252 is actual progress:frame identity repaired,
16/16 real-video hash replay and130 regressions pass;not new head acceptance.

## Distinct hypothesis and strict scope

0219's skin-only features were sparse;0220-23's chained skin tracks failed
independent rigidity/closure.0233-35 freeze the local patch family.0251's
source-geometry photometric pose recipe is closed. Do not resurrect these tools,
COLMAP,downloaded learned models or another local-refinement setting.

Test an external motion-reference assumption **before** any reconstruction:
can visible cap texture support a two-view geometry that also explains untouched
face correspondences? The cap is not assumed rigid or anatomically meaningful.
It may deform,slip,contain repeated patterns or yield planar/poor matches. This
is not a skin-mask/threshold sweep to rescue0219,does not rerun its reconstruction,
and does not permit hair/cap geometry to become an output head. A failure stops
this external-proxy recipe;do not adjust its regions,frames or matching knobs.

## Fixed input,pre-fit review and one variable

Only original authorizedcase001 video and0252 exact sequential RGB hashes.
No source scan,bone,case002 geometry/video,learned predictor,training or upload.
Decode from zero and retain exact ordinals0,60,120,240,300,360,420,540,600.
Six pairs fixed now:(0,60),(60,120),(240,300),(300,360),(360,420),(540,600).
These are development views,not newly unseen acceptance images.

Before extracting features,review those native images and freeze separate
conservative cap-interior and face-interior polygons as private input annotations.
This manual source-region selection is not an automatic production segmenter.
No descriptor/match/epipolar residual may influence the polygons. Source cap
wrinkles,hair/room boundary and facial-expression concerns must remain explicit.
Freeze the source-region review with polygon/control hashes before executing.

Main variable:external cap reference instead of unverified skin-track identity.
Use already installed OpenCV5.0.0 SIFT defaults,nfeatures4096,CPU4 threads.
No learned checkpoint or new dependency. Deduplicate centers deterministically
at5px separation before matching to avoid repeated orientation counts. Require
descriptor support conservatively inside its polygon (distance>4.5*keypoint size,
minimum8px);this heuristic is not a proof of compact descriptor support.
Exact brute-force L2 mutual nearest-neighbor matching with bidirectional ratio
<0.8. No temporal chaining,epipolar-guided matching or endpoint refinement.

Sort cap matches by source(x,y),then immutable alternating IDs:even fit F,odd
validate F. All direct face matches are held away from F estimation. Need>=30
cap points per partition and>=30 face matches,each held population spanning>=50px
in both coordinates in both images. All matched face points are scored without
RANSAC,residual deletion or snapping. Exclusions occur only at fixed appearance/
region checks before fitting,with every count recorded.

Fit F only to even cap points using FM_RANSAC,1px,confidence.999,max10000,seed253;
need>=30 cap training inliers. Score **maximum of both** point-to-epipolar-line
distances,not Sampson alone. Require p95<=3px for held cap and all face matches
in every pair. Also report2px homography support on cap-training matches;
bilateral intervals0-120 and240-420 each need at least one pair with fraction<.8
before a later unknown-focal camera initialization can even be considered.
Pure/near-planar or poorly distributed supports cannot establish3D cameras.

One120s scoring run after a60s input-review decode. Math self-checks must compare
analytic known3D F against OpenCV line distances,fit on independent nonplanar
proxy points and reject displaced held-face controls. Save input,producer,
protocol,annotation and library hashes,all match populations/F/errors and actual
source-region/match review. No retries,seeds/pairs/ratio/mask/threshold sweep.

Pass authorizes only a separately registered common-focal/proper-camera and
independent projection check. Epipolar consistency cannot verify position along
a ray,metric structure,cap rigidity,full3px reprojection,2mm anatomy or head
likeness. No head fit or production-default change occurs here. Failure closes
the assumption before another route and requires0250 cleanup of exclusive code/
raw artifacts after compact evidence and a Git source recovery point.

## Primary sources and limitations

[OpenCV epipolar tutorial](https://docs.opencv.org/4.x/da/de9/tutorial_py_epipolar_geometry.html)
describes F and feature-match sensitivity/planar degeneracy;
[SIFT documentation](https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html)
describes descriptor locality,orientation duplicates and ratio matching.
These are method/API references,not proof that this person's cap is rigid or
our matches accurate. Installed5.0.0 API/version is checked locally rather than
assuming redirected4.x docs define exact current binary behavior. No third-party
sample implementation is copied. This external-proxy proposal is our inference,
not an established clinical or reconstruction-quality result.

## Actual single-run result and enforced stop

One2.405s scoring run completes(exit0). All synthetic analytic/OpenCV line
controls pass. All9 exact sequential source-frame RGB hashes match0252.
The source-only region sheet was reviewed before feature extraction;the final
all-matches sheet was actually viewed after execution. No annotation/region,
pair,ratio,descriptor setting or seed is changed after results.

| Pair | All cap matches | Fit / held cap | All untouched face matches |
|---|---:|---:|---:|
|0-60|0|0 /0|0|
|60-120|17|9 /8|1|
|240-300|1|1 /0|2|
|300-360|1|1 /0|1|
|360-420|14|7 /7|0|
|540-600|3|2 /1|1|

No pair reaches30 fit cap observations;no F is fitted. No epipolar p95,
homography degeneracy,focal,pose,3D or millimeter accuracy can consequently be
reported. This rejects the **specific conservative-region/default-SIFT direct
external-proxy observation recipe**,not the mathematical possibility of cap
rigidity,all feature matching or reconstruction. The result exposes insufficient
direct cross-view associations rather than measuring cap slippage/deformation.
After support/duplicate filtering,source-cap counts are30-180 versus140-425 raw
detections,and face counts1-35 versus12-75 raw. Texture density is not usable
cross-view identity. No fallback to chained flow,larger regions or ratio changes.

Preparation initially decoded and saved the9 correct frames but hit a str/Path
type error during its final source-hash metadata write. The recovery rereads
the existing PNGs,verifies each original sequential RGB hash and original video
digest,then writes the missing input record without redecoding or substitution.
That engineering recovery and original error are retained in the private archive.
It does not alter the actual single scoring run or hide a failed model attempt.

Source recovery commit:`de9b5f7`. The exclusive runner and raw temporary source
PNGs/review duplicates are retired after compact private archive verification.
`assets/private/closed-experiments/0253/evidence.zip` retains reports,full match
arrays,exact annotations/control hashes,execution logs,pre-result protocol and
two bounded region/match review sheets. No new dependency/checkpoint exists to
uninstall. Original video,intake,0252 audit/shared fix,successful scan evaluators,
case002,production defaults and unrelated0207 draft remain untouched.

The full-head goal remains unachieved. No video head or camera is promoted.
Another region/density/temporal-hop variant is not justified by this result;
a distinct observation mechanism must first demonstrate sufficient independent
camera information. No image-only/fitting-residual success may replace the
original3px reprojection,2mm scan-region and actual whole-head visual gates.

Closeout verification:817,044byte private archive,CRC checked,SHA256
`69e38e464f366160a05a6ed599040378d325fb9849b9cc444f7e6785b40cf2ec`.
After checking the terminal process and resolved non-symlink private target,
remove20 raw files totaling7,341,667bytes plus the tracked exclusive runner.
This is logical file size,not a measured free-disk delta. Ten protected source/
consent/intake hashes remain unchanged.130 retained tests pass in4.989s;
Git whitespace check passes. The archive preserves bounded evidence,not the
deleted source PNGs;those can be regenerated at their saved exact ordinals.
