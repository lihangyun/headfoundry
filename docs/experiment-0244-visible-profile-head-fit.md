# Experiment0244: shared safe video head with true visible profile envelopes

Date:2026-10-19. Pre-registered before new observations/poses or shape fitting.
Status:UNVERIFIED. Overall complete-head goal remains active.

0243 supplies measured bilateral visible profiles;0242 rejects treating the
frontal420 learned semantic points as exact material observations. Test a
different image observation model: projected **view-dependent skin envelopes**
of one shared300-D native anatomical head. No free local patch,surface warping,
scan-based pose/coefficients/initialization or new learned asset is introduced.

Start from the safe VIDEO-only0241 coefficients/geometry,focal937.2157px and
existing frontal832 camera. They are rejected experimental estimates,not
calibrated cameras or a trustworthy identity. This is a bounded correction of
that video baseline,not a controlled estimate of the effect on0241's old loss.
0241 source/scan evaluation directory and all patient STL/oracles are forbidden
to inference. Use only the already cleared exact FLAME2023 Open identity asset
and locked local MediaPipe task. No training,upload,case002 or default changes.

Use exact authorized0243 video frames139/416 as fitting profiles and69/347 as
development held views. The latter were seen in coverage inspection,not fresh
unseen population data. Fit profiles preserve all213 nominal source rows and
their original uncertainty arrays. Held traces use the same gradient-ridge
algorithm,scales,ROIs and precision checks for the respective direction:
right:[400,630,590,843],left:[120,630,320,843]. Review all overlays before fitting;
failed/visibly wrong held observations abort this configuration,no ROI search.

Estimate one initial proper positive-depth pose per4 views by ordinary iterative
PnP+RefineLM at the frozen focal,using original eligible IDmod5!=0 training
semantics from the current baseline and native landmarker pixels. This is only
a coarse initializer,not precise material evidence or a loss term. Do not fit
those semantic pixels again or claim their projection proves true cameras.
Keep held69/347 poses fixed after this initialization; never optimize held
contours/poses or use them to select a candidate. Inspect initial model-envelope
and photo overlays to confirm nasal/lip/chin rather than unrelated ear/neck.

Fit300 shared coefficients,bounded[-3,3],and6 pose increments for each of139/416.
Focal,principal point(360,640),frontal832 camera,and all other0241 cameras stay
unchanged. Pose incrementsq bounded[-3,3]:rvec=rvec0+.03*q_rot,
tXY=tXY0+.005*q_xy,tZ=tZ0*exp(.03*q_depth). Start at baseline coefficients and
zero pose increments. Objective is ordinary squared training-profile horizontal
row residuals/2px plus unit Gaussian beta change and unit Gaussian poseq.
No semantic pixel,scan,detector relativeZ,held row/view or robust loss in fitting.
Within each213-row fitting trace,indicesmod5==0 are held rows; all are evaluated
afterward. Adjacent row validation is not independent image/camera evidence.

Compute actual front/back-facing occluding edges of the complete current mesh,
retain largest native connected skin component,and select anterior outer
envelope at each exact observed pixel-center row. Reassociate each evaluation;
do not fix a vertex/barycentric material anchor per image row. Use tested
perspective-correct envelope derivatives plus analytic pose derivatives; check
by finite differences before the single real fit. Confirm final selected
supports are exact first-hit skin on the full mesh,not merely facing edges.
Missing/clipped/uncovered rows or lost final visibility fail rather than trim.

Hard whole-mesh native guards are unchanged:normaldot>=1e-6,area ratios
.20001..4.99999,original coefficient bounds. Start constraint generation with
faces whose **video baseline's own** normaldot/squared-area inequalities are
within1e-4 of a boundary,not0240's source-derived face list. Add only new
violations from this candidate,at most5 rounds,restarting from baseline.
Hard frontal representation protection:each of the original420 material
attachments must remain within2px Euclidean displacement of its own baseline
projection at frozen832 camera. These are **model self-preservation** anchors,
not claimed anatomical/photo correspondences. They constrain width/height
regression without calling detector data correct or changing the frontal camera.

SLSQP analytic objective/constraint Jacobians,ftol1e-8,maxiter120 per round,total
180s. Preparation/initial review60s;render60s. One fixed configuration,no
coefficient/ridge/focal/pose/point-set sweep. Require optimizer success,all mesh
guards,<=2px frontal drift,all-row coverage/first-hit visibility,and held row
and fixed-held-view p95<=3px before any technical promotion. Even a safe output
failing projection may be exported only as NOT-ACCEPTED experimental geometry.

After inference terminates,freeze arrays/OBJ/hashes. A separate evaluator uses
the already declared0241 **same evaluation4x4** for both original baseline and
new candidate and the unchanged0237 sample/region masks. No new alignment,
ICP,regional pose,trim or scan feedback. Measure all7 facial groups and entire
source/reverse distances. Actual common-camera baseline/candidate/source clay
plus original-photo overlays are mandatory before any improvement claim.
Partial profile traces cannot supply whole-head silhouette IoU. The native62
boundaries,unobserved posterior/cap and global collision uncertainty remain
explicit incomplete gates,even if facial distances improve.

## Actual preparation stop: no profile detector initialization

Locked runtime1.0.1 returns0 faces on exact139,416,69 and1 on347. Both fitting
profiles therefore lack the declared coarse PnP initializer. The process stops
before preparing any pose,shared-head optimization or scan evaluation. Preserve
the original four records and nonzero exit at
`assets/private/visible-profile-head-0244/`. No input/ROI/task/confidence change,
fabricated landmark,scan pose or nearby-frame substitution follows. Execution
of this configuration is `REJECT`; no new head/result or geometry gain exists.

The new visible-envelope/pose and frontal-protection derivatives pass two
independent finite-difference tests;193 total unit tests pass. This mathematical
readiness does not bypass the failed input precondition. Next distinct mechanism
is detector-free profile camera initialization from native anatomical axes and
the observed anterior nose extremum,then fixed-head contour pose registration.
That new initializer needs a separate pre-registration; do not resume0244 as if
its detector succeeded. Existing patient-scan/default/case002 boundaries hold.
