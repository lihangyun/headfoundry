# HeadFoundry

HeadFoundry is a clean-room, quality-first multi-view 3D head reconstruction project. It does not reuse PeekSim code, KeenTools outputs, or proprietary service behavior.

The first milestone is deliberately narrow: prove that camera projection can be recovered and measured reliably. Later user authorization permits unaccepted experimental geometry while that gate remains failed; it does not waive acceptance. The repository contains a normalized-DLT reference, fail-closed rights/capture manifests, a commercial-VGGT output adapter, and camera quality gates.

## Current status

- Experiment 0168 inspects every frozen held camera track on the original local photos. The three largest 7.25–7.59 px residuals lie on eyebrow hair or textureless brow skin, and the 11-track set is concentrated around eyes/brows with no profile, nose-tip, chin or rear-head validation. The numerical camera gate remains failed; the error cannot yet be isolated to camera pose. Predeclare stable distributed material correspondences before another solve.
- Experiment 0167 directly audits the current camera archive against 11 frozen, previously held-out front/oblique feature tracks: third-view p95 is 7.374 px versus the 3 px gate, with positive depths. A training-only bundle fit from these cameras reaches 3.521 px train p95 but 7.545 px held p95 at its 300-call budget, nearly the old initialization's result. Camera promotion remains `REJECT`; inspect match validity before further pose fitting.
- Experiment 0166 tests a tapered deformation of the existing scalp instead of another closed mask solid. Normal and vertical offsets improve front crown coverage but overshoot both side crowns; a single scalar lift is `REJECT`. The photo hairline, bare scalp and unaccepted camera are not interchangeable evidence, so the next shape/camera test must protect facial landmarks across views.
- Experiment 0165 crops the rejected hair hull to upper scalp and rear bun. It removes lower rear blocks but leaves a hard horizontal scalp cut and an implausible bun connection in both real side overlays. This branch remains `REJECT`; the next hair attempt needs an explicit surface and gathered-flow representation, not another mask-solid parameter sweep.
- Experiment 0164 rejects a five-view hair visual hull. Exact-camera replay passes, but real overlays show a rigid cap, above-ear seam and blocky bun/nape; stronger smoothing removes striping without fixing those shapes. The private meshes/renders are preserved for inspection, not promoted. Hair needs explicit scalp/hairline and swept-to-gathered structure rather than a solid carved from dark pixels.
- Experiment 0163 rejects a convex bun-to-scalp bridge: side dark-hair ROI IoU rises to 0.709/0.788, but corrected five-view renders reveal an unnatural horizontal tube. The shape is `REJECT` despite the larger score. Future hair geometry needs a nonconvex scalp/hairline and gathered connection, assessed across views rather than by area overlap alone.
- Experiment 0162 adds a local-only three-dimensional bun proxy to the unchanged current head. Side bun-region mask IoU rises from zero geometric coverage to 0.610/0.552, while the front face stays unobstructed. Corrected five-view renders show a disconnected smooth ball in the obliques, so the hair-volume hypothesis is `PARTIAL_SUCCESS` but full-head/default promotion is `REJECT`; a continuous scalp-to-bun form is next.
- Experiment 0161 fixes the exact-camera Blender OBJ-axis import error: previous Blender overlays showed the wrong side of the head and are invalid visual evidence. The corrected renderer checks original OBJ coordinates (maximum error 5.96e-8), outputs separate clay/overlay views and passes subpixel camera projection replay. Corrected face and side views are closer than the invalid renders suggested, but subject identity, hair, eyes and neck remain incomplete; no geometry or camera is promoted.
- Experiment 0160 independently measures the *actual rendered* facial boundary at all 17/16 frozen pure-profile rows. Mean absolute errors are 4.24/4.94 px, so the suspected hidden-edge scoring bug is rejected. This only measures brow-to-chin exterior contour, not the full head or interior anatomy. The next bottleneck is reliable subject-specific central-face shape and posterior-head evidence, not another pass over the same sparse outline rows.
- Experiment 0159 rejects the classical-stereo geometry route: two independently triangulated front/30° point clouds yield only 443 points within 0.03 model units, and their fused cloud covers just 7/17 left and 7/16 right unused-profile contour rows. Covered-row errors are 34.21/21.41 px; local overlays show missing mouth/chin support. Execution is `TECHNICAL_CHECK_PASSED`, geometry is `REJECT`. Next use pure-profile contours directly as fixed-camera shape evidence, with held rows and five-view visual review.
- Experiment 0158 establishes a model-free dense-photo route: fixed experiment-0132 front/±30° cameras rectify successfully and 11-pixel semi-global matching reaches 4.06/4.64 px median disparity error on reviewed central correspondences, with 50.2%/51.7% valid masked-face coverage. Correspondence feasibility is `TECHNICAL_CHECK_PASSED`; depth and geometry remain `UNVERIFIED`. Next triangulate only consistent disparities and validate them in the unused pure-profile views.
- Experiment 0157 transfers all 82 paired CC0 controls onto the current closed mesh and fits them with fixed cameras. A profile-weighted solve safely improves every aggregate outline/profile metric, but the untouched profile rows reject it: left held error worsens 4.247→4.643 px and right 4.387→4.526 px; exact Blender overlays show no confident identity gain. Mapping/solver are `TECHNICAL_CHECK_PASSED`, the subject candidate is `REJECT`. Do not train a neural decoder on the same rejected source manifold—it cannot create missing identity capacity.
- Experiment 0156 converts the 348 locked targets into 82 paired neutral controls and generates 256 deterministic synthetic identities. Maximum displacement is 0.1914, minimum area ratio 0.4117, no triangles reverse and a fixed 12-sample front/profile sheet shows coherent heads with modest diversity. Generation/safety are `TECHNICAL_CHECK_PASSED`; coverage and subject quality remain `UNVERIFIED`. The next gate fits this piecewise nonlinear manifold directly before spending effort on a neural decoder.
- Experiment 0155 expands the same pinned official CC0 MakeHuman source from 92 selected assets to 348 reviewed face/head targets, verifies every explicit CC0 header and SHA-256, and maps them to one 4,459-vertex head topology. Rights/lock/conversion are `TECHNICAL_CHECK_PASSED`; identity quality remains `UNVERIFIED`. This is the deterministic source basis for a controlled synthetic nonlinear identity prior, not a claimed subject improvement.
- Experiment 0154 tests eight coherent macro identity modes (forehead/mid/lower depth, face/cheek/jaw width, chin height and taper), first shared and then independently on the two visible hemispheres. Both solves converge, but every nonzero step trades right-side improvement for left train/held regression; removing symmetry coupling does not resolve it. Execution is `TECHNICAL_CHECK_PASSED`, both representations are `REJECT`. Stop adding hand-authored scalar modes—the next route needs a coherent nonlinear 3D identity prior or an independently trained synthetic-data prior.
- Experiment 0153 replaces the broad mouth field with six anatomical layers. An experimental 0.20-scale candidate improves both fitted profiles, combined held evidence and both oblique outlines; maximum displacement is 0.00371, minimum area ratio 0.953 and no triangles reverse. This is `TECHNICAL_CHECK_PASSED` and numerical `PARTIAL_SUCCESS`, but exact Blender overlays show no confidently visible identity improvement, so visual/default promotion is `REJECT`. Stop tuning millimetric local depth fields on this generic mesh; the next representation needs coherent whole-face identity capacity.
- Experiment 0152 gives the two visible facial hemispheres separate smooth lower-face capacity while fixing every camera and requiring corresponding 35° transfer. The smallest nonzero step improves both fitted profile subsets, the left held subset and both oblique outlines, but immediately worsens the right held subset from 4.594 to 4.608 px and degrades thereafter. Solver evaluation is `TECHNICAL_CHECK_PASSED`; every nonzero geometry is `REJECT`. Side coupling is not the missing capacity—the next basis must distinguish upper lip, seam, lower lip, labiomental groove and chin.
- Experiment 0151 verifies that the tiny experiment-0150 camera step does not win by hopping to unrelated apparent-contour edges: all 3 nose, 7 mouth and 4 chin samples retain a shared baseline-edge vertex, with at most 0.000130 model-unit support motion. The read-only audit is `TECHNICAL_CHECK_PASSED`, while anatomical correspondence remains `UNVERIFIED`. The next test keeps cameras fixed and gives the two visible facial hemispheres softly separated lower-face shape capacity, accepted only with same-side oblique transfer and all existing protections.
- Experiment 0150 fits a tiny right-profile camera perturbation on interleaved mouth rows and line-scans it under near-eye, subnasale, nose, chin, cheirality, focal and rigid-matrix protection. A feasible nonzero step exists, but it lowers held-mouth error by only 0.071 px (6.504→6.433, about 1.1%) with rotations below 0.012°. The diagnostic is `TECHNICAL_CHECK_PASSED` and the direction is `PARTIAL_SUCCESS`, but camera promotion is `REJECT`: camera error cannot explain the visible lower-face deficit. Keep cameras fixed and move to correspondence/anatomical shape capacity.
- Experiment 0149 separates the rejected bilateral lower-face update into one shared neutral scale and three bounded per-profile nuisance modes (jaw hinge, lip protrusion and closure), with cameras fixed. The corrected solve converges, but right transfer still worsens from 4.594 to 5.320 px and the right nuisance mesh reverses 536 triangle normals. Solver replay is `TECHNICAL_CHECK_PASSED`; both neutral and adjusted candidates are `REJECT`, and expression causality remains `UNVERIFIED`. The next discriminating test is a tiny physical right-profile camera perturbation fitted on the mouth but accepted only if independent eye/nose/ear/chin evidence is preserved.
- Experiment 0148 localizes the 0147 bilateral conflict: three consecutive right-profile subnasal/lip transfer samples regress together (+0.030/+0.123/+0.077 px), while two lower-chin samples improve; four of five left transfer samples improve. Visual inspection finds no single obvious bad contour point. Read-only replay is `TECHNICAL_CHECK_PASSED`, geometry remains `REJECT`, and expression/pose causality is `UNVERIFIED`. The next representation must separate small per-view mouth-expression nuisance from neutral identity rather than baking one photo into asymmetric geometry.
- Experiment 0147 tests a four-knot bilateral mouth/chin/jaw depth spline with fixed cameras and hard nose, eye, frontal/oblique and mesh protections. The smallest nonzero step improves both fitted sides and the left interleaved transfer subset, but immediately worsens the right transfer subset (4.594→4.607 px), with increasing conflict at larger scales. Safety and other protected evidence pass, so the runner is `TECHNICAL_CHECK_PASSED` but every nonzero geometry is `REJECT`. Zero remains selected; next re-audit right-profile lower-face semantics/camera uncertainty rather than weakening the bilateral guard or adding another shape family.
- Experiment 0146 partitions the unchanged bilateral profile evidence into semantic regions while excluding hair, cranium and artificial neck cuts. The nose is already the best region (0.84/3.10 px mean), whereas mouth (3.44/5.76 px) and chin/jaw (5.12/4.22 px) remain the consistent bilateral deficits; the right upper bridge is a separate 8.46 px issue. Audit replay is `TECHNICAL_CHECK_PASSED`, but the observations are existing fitting evidence and no geometry is promoted. The next candidate must be a structured mouth-plus-chin/jaw mode with nose, eyes, frontal/oblique evidence and mesh safety protected—not another nose field or global scale change.
- Experiment 0145 converts the unchanged 0132 matrices into exact Blender cameras and produces private semi-transparent photo/clay overlays. Independent Blender projection replay is below 0.00013 px maximum in all five views, so the conversion is `TECHNICAL_CHECK_PASSED`. The overlays reject any whole-head success claim: frontal envelope is broadly coincident, while pure profiles expose major cranial-depth, posterior-skull/neck and cut-boundary disagreement. Selected 3–5 px facial rows never certified the complete head; the next gate is region-semantic profile evidence, not more nose/lip-only tuning.
- Experiment 0144 installs Blender 5.2.1 LTS and adds a non-overwriting, hash-reported five-view clay diagnostic. The real experiment-0132 OBJ produces a reopenable `.blend` plus fixed front/35°/90° renders; the first wrong-axis run is preserved and excluded. The rendering path is `TECHNICAL_CHECK_PASSED`, while the visibly generic identity, open lips and incomplete eyes remain `UNVERIFIED`; Blender does not promote geometry or unlock texture work.
- Experiments 0142–0143 install and safely convert the official CC-BY-4.0 `FLAME 2023 Open` identity model: the source ZIP, pickle and safe NumPy conversion are independently locked, and the real 5,023-vertex/9,976-triangle/300-direction adapter is `TECHNICAL_CHECK_PASSED`. Fixed-camera identity, similarity and topology-transfer trials remain visibly generic; the best transfer leaves bilateral profile errors at 32.22/30.42 px versus about 3.62/4.92 px for the current 0132 result. Every FLAME identity/default promotion is `REJECT`; retain it only as a legal standard topology/rig prior.
- Experiments 0140–0141 test the remaining front-camera-ray central-depth family without changing the experiment-0132 cameras, topology or safeguards. A direct 20,362-vertex surface direction is forced down to 0.000300 maximum movement and is visually imperceptible; smoothing that direction selects zero. Direct optimization of 30 smooth RBF fields also selects zero: its first nonzero step slightly improves both profiles but worsens one oblique outline and the right reviewed-material mean, while the solver hits its iteration limit. Replays are `TECHNICAL_CHECK_PASSED`; every candidate/default promotion is `REJECT`. Stop adding local ray fields—the next route requires a real identity prior and independent validation.
- Experiment 0139 adds the two locked CC0 MakeHuman eye components to the current head with every head vertex and camera unchanged. Both helpers are closed manifold components and render in all five views, replacing the conspicuous empty sockets. This is `TECHNICAL_CHECK_PASSED` and `PARTIAL_SUCCESS` for visible completeness, but `REJECT` for identity/default promotion: the eyes remain generic, disconnected and untextured, with no subject gaze or iris.
- Experiment 0138 adds the reviewed profile material points to the six-field central-depth fit. A safe nonzero step improves the left material mean by 0.37px while the right is unchanged, but the optimizer does not terminate successfully and native nose/lip crops are visually indistinguishable. Numerical replay `TECHNICAL_CHECK_PASSED`, visual promotion `REJECT`; stop retuning this limited six-field basis.
- Experiment 0137 replays the 0135 profile-camera direction on front-lifted, visually reviewed near-eye and lip/subnasale material points. The 0.76 silhouette-selected camera worsens their left/right means from 9.0087/10.2408 px to 9.1528/10.8358 px; the best of 101 fixed scales is zero. The replay is `TECHNICAL_CHECK_PASSED`, but the provisional full-profile landmarks are not calibration truth. Experiment 0135 remains `PARTIAL_SUCCESS` only as a contour diagnostic and `REJECT` for camera promotion; subject-specific central geometry under the 0132 reference cameras is next.
- Experiments 0133–0136 test the next central-face routes without weakening safeguards. Graph smoothing selects zero; a stable three-view MediaPipe depth consensus conflicts bilaterally when attached to the current head; a dense-row profile-camera correction transfers to withheld rows but remains same-photo evidence; and an independent Apache-2.0 468-point face patch still fails the right profile badly. Technical checks pass where stated, the camera candidate is only `PARTIAL_SUCCESS`, and all geometry/default promotion remains `REJECT`. Independent right-profile camera/correspondence evidence is now the next gate.
- Experiment 0132 replaces generic central-face sliders with six compact subject-derived nose/lip depth fields while freezing cameras and outer shape. Both corrected side-profile means and both oblique central-point means improve, all protected eye/outer-outline evidence is unchanged, and the mesh remains valid. Enlarged bilateral renders show a real nose/lip contour movement, but the lip stays angular/generic and one coefficient saturates. Technical path `TECHNICAL_CHECK_PASSED`, candidate `PARTIAL_SUCCESS`, default promotion `REJECT`; next resolve neutral-lip anatomy with an evidence split, not more unconstrained point fitting.
- Experiment 0131 jointly fits nine audited CC0 whole-head/central-face directions under per-eye, bilateral-profile and mesh-safety protection. All four fitted outline groups and both profiles improve, every protected eye error is numerically preserved, and the mesh stays valid; actual five-view inspection shows a modest outer-shape change but still-generic nose, eyelids and lips. The route is `TECHNICAL_CHECK_PASSED`, the experimental candidate is `PARTIAL_SUCCESS`, and default promotion is `REJECT`. Next evidence must be subject-specific central facial structure, not another generic macro-target expansion.
- Experiment 0130 transfers one hash-locked CC0 lower-lip target through exact source IDs and the current subdivision/closed-patch construction. Boundary-only transfer safely improves both profile means at full authored strength, but the five-view appearance change is too small; interior transfer gains amplitude only by reversing triangles and regressing the right profile. Asset/transfer checks `TECHNICAL_CHECK_PASSED`, safe candidate `PARTIAL_SUCCESS` numerically and `REJECT` visually. Stop isolated generic lip-target tuning and move to broader subject identity structure.
- Experiment 0129 sweeps one localized lower-lip relief scalar on the protected experiment-0128 mesh. Only zero preserves every 0128 diagnostic; the visible -0.008 trial trades a small right-profile regression for left-profile gain and still looks like a generic bump. `TECHNICAL_CHECK_PASSED` as a sensitivity test, `REJECT` for geometry promotion. The next route needs anatomically structured lip freedom, not finer tuning of this scalar.
- Experiment 0128 finds a stable nonzero coupled update with all eight protected eye anchors and both profile means improved; minimum triangle area ratio is 0.957. Actual five-view inspection still shows generic identity and a flat lower lip. This is `PARTIAL_SUCCESS` for constrained fitting evidence and `REJECT` for baseline promotion; the missing issue is shape capacity, not permission to relax safeguards.
- Experiments 0126–0127 fit the stable reconnected patch jointly with pose, then test explicit view-mean constraints. Geometry remains stable, but the constrained solve reports failure and one eye worsens despite near-preservation of its view mean. Both candidates are rejected; per-anchor protection cannot be replaced by aggregate error checks.
- Experiment 0125 confirms that the same deformation on reconnected triangles improves minimum area ratio from 0.233 to 0.884 and removes the tested area/normal failures. The optional tested NumPy diagonal helper is available; defaults remain unchanged. Actual five-view identity remains generic, so this is technical stability progress, not likeness acceptance. 99 tests pass.
- Experiment 0124 traces the worst deformation-area failures to nearly collinear patch triangles and improves internal planar connectivity with vertices/boundary fixed. Minimum triangle quality rises from 0.000074 to 0.002979. A recomputed 3D candidate is unverified pending rendering and deformation checks; no likeness or default promotion.
- Experiment 0123 couples three compact actual-surface depth fields with oblique pose. The large free-point eye shift is avoided, but left eye/right profile regress and minimum triangle area ratio falls to 0.215. Candidate rejected; smaller aggregate errors do not waive protected-view or geometry checks.
- Experiment 0122 applies the 0121 camera hypothesis to the unchanged actual head. Eye support errors jump from 5.47/4.85 to 25.24/23.47 px despite continued visibility. Reject standalone camera transfer; future coupled fits must constrain actual shared mesh supports, not freely relocated points.
- Experiment 0121 fits physical oblique rotations using eyes/nose only. Excluded mouth errors fall from 7.82/4.78 to 1.92/1.09 px, but eyes and chin worsen, so the camera candidate is rejected. Free-point depth changes are not an actual-head improvement; review contour-versus-material correspondence before coupled fitting.
- Experiment 0120 checks eleven eye/nose/mouth/chin correspondences under the current cameras. Free-ray vertical residuals are near zero at eyes, positive at nose/mouth, and negative at chin. Do not transfer a mouth-derived uniform image shift to the whole face; no camera/shape candidate or quality promotion follows from this diagnosis.
- Experiment 0119 adds provisional interior-lip cross-view support with cameras and topology fixed. Both profiles regress and lower relief remains flat. Even free frontal-ray depth fitting retains 4–8 px mostly vertical oblique errors, so these correspondences cannot be treated as exact geometry targets. No candidate promotion.
- Experiment 0118 fits only profile camera rotations outside the mouth on the unchanged mesh. Training errors decrease but excluded mouth errors increase on both sides (6.03 to 6.23 px and 4.38 to 5.58 px). Pose-only promotion is rejected; no camera or shape default changes.
- Experiment 0117 corrects 13 misplaced mouth-profile observations without changing the model or fit settings. Actual likeness remains generic and lower-lip relief remains flat; no promotion. A photo-only perturbation check also penalizes restored relief, so removing the prior alone is not a supported fix. Historical sparse profile scores are not accurate boundary ground truth; preserve original and corrected evidence separately.
- Experiment 0116 reduces the experimental patch's worst seam angle from 102.78 to 19.03 degrees with the lip core fixed. Actual renders retain flat/generic lip shape; relative triangle changes and slight right-profile regression prevent promotion. Stop collar-only tuning as an identity route; photo-consistent relief remains unresolved. No baseline or camera gate changed.
- Experiments 0114–0115 replace the failed mouth opening with a locally stitched neutral disk and test metric-aware interpolation. Actual renders eliminate the opening and substantially reduce numerical striping, but fitted lip relief becomes flat, the left profile regresses and identity remains generic. Neither mesh is promoted. The tested polygon/FEM helpers are technical progress, not an expression-ready or accepted reconstruction.
- Experiment 0113 re-establishes sampled gap heights on the actual smooth surface and tests a bounded monotone closure map. The frontal slit narrows, but both profiles regress; half strength collapses some triangle areas, and stronger closure introduces mouth-corner intersections. Both trials are `REJECT`. The tested map is not an anatomical contact or collision solver; 94 tests pass, with no identity promotion.
- Experiment 0112 reproduces mouthClose intersections on the untouched base, then independently tests geometric subdivision of the current head. A tested NumPy Catmull-Clark helper reduces faceting, but the mouth remains open/generic and the left profile worsens, so neither refined mesh is promoted. Actual five-view comparisons exist locally; smooth-surface fitting and contact remain unresolved.
- Experiment 0111 tests a separately locked CC0 mouth-close expression on the actual head. All nonzero trials worsen the right profile and introduce sampled lip intersections, including a trial with no reversed triangles. Enlarged five-view renders still fail natural closure; promotion is `REJECT`. The asset is not enabled as a default or accepted identity solution.
- Experiments 0109–0110 separate coarse-mask exterior sheets from an inset facial patch, then test frontal image depth as one bounded template-shape prior. Interior support removes long sheets only by excluding non-skin/outer regions; it is not a full head. The new head candidate regresses the left profile and remains generic/open-mouthed, so promotion is `REJECT`. Neutral mouth configuration remains unresolved; 88 tests pass.
- Experiment 0108 reuses unchanged raw z depths/cameras with exact pinhole rays. Own-view projection becomes exact by construction, but dense transfer p95 remains 91.93 px and inspected cross-view sheets persist: `REJECT`. Ray approximation is not the sole failure; do not fuse the patches or count self-projection as calibrated geometry.
- Experiment 0107 supplies one existing 1800 px focal hypothesis to the same Apache model. Returned intrinsics do not enforce it, camera p95 worsens to 51.48 px and actual cross-view surfaces remain malformed: `REJECT`. A separate audit finds 18–26 px own-view disagreement between native ray maps and their fitted pinhole cameras. Isolate this representation discrepancy before more inference or fusion; 88 tests pass.
- Experiment 0106 executes the exact Apache MapAnything checkpoint locally on all five photos. Raw held-out camera p95 is 48.58 px and focal plausibility fails; actual open-surface cross-view renders are incoherent. Camera and visual promotion are `REJECT`. The offline asset-locked runner and rigid pose conversion are tested (87 tests); conditioning/calibration diagnosis is next, not raw surface fusion.
- Experiment 0105 reproduces the early masked SIFT failure and tests affine/domain-size-pooled extraction. One frontal/oblique pair gains 26 inliers, but all profile connections fail and both runs produce no sparse model. COLMAP dense stereo is not unlocked; next evaluate the separately identified Apache MapAnything dense-geometry candidate.
- Experiment 0104 verifies 44 CC0 nose/lip assets and reduces 32 signed controls to eight local directions. Bounded fitting lowers profile/point errors without triangle reversals or original visible-support loss, but actual five-view and enlarged mouth renders remain generic/open/angular. Visual promotion is `REJECT`; the numerical report is `UNVERIFIED`, and these are fitting/selection metrics, not held-out validation. Independent sparse multiview feasibility is next.
- Experiment 0103 locks six additional CC0 macro shape assets and tests both nonnegative and centered-difference bases. Profile metrics move slightly, but protected frontal/anchor evidence regresses or forces a zero step, and five-view identity is unchanged. Broad macro shape is rejected as the missing identity representation.
- Experiment 0102 dynamically updates visible lip-seam targets and lowers the fixed 51-target mean from 5.50 to 1.97 px, but loses three originally visible oblique supports and fails the enlarged visual check: the mouth remains an angular open shelf and identity stays generic. Candidate rejected; stop this provisional seam representation.
- Experiment 0101 fits 51 source-visible photo seam constraints, but six become occluded and the area floor stops further steps. Actual five-view identity remains unresolved; candidate rejected for promotion. Visibility/curve targets must update during fitting with fixed-support reporting.
- Experiment 0100 extracts and visually inspects three 41-point photo lip-seam curves using bounded dark-line tracing. They broadly follow the visible closed seam without search-boundary hits; localization and cross-view correspondence remain unverified. No mesh change.
- Experiment 0099 audits the bounded candidate: mouth-profile means improve and sampled sections have no proper crossings, but enlarged views retain an open/angular mouth and hide the old lower seam sample. Internal gap reduction has not achieved natural closure; visible lip-line fitting is next.
- Experiment 0098 bounds pair/profile iterations and updates silhouette support. Both final profile means decrease (3.54/6.52px), total movement stays below 0.03 and area ratio is 0.598; actual five-view identity remains unverified. No promotion or collision-free claim.
- Experiment 0097 integrates sixteen bilateral photo contour observations with central surface pairs. Right profile improves but left slightly regresses and displacement reaches 0.0395 template units; no promotion. The pair-only planar audit found no sampled proper crossings, not complete collision freedom.
- Experiment 0096 adds tested relative surface-pair constraints and runs thirteen real central lip pairs. Gaps shrink with protected surroundings and valid triangles; 82 tests pass. Actual five-view likeness remains unverified; soft pair offsets do not provide collision-safe contact or complete closure.
- Experiment 0095 finds corner-region section changes and distinguishes closest surface pairs from the visible seam. Most nearest pairs are hidden in obliques; they cannot substitute for photo landmarks. Contact and visible-seam constraints remain separate unfinished work.
- Experiment 0094 traces 26 central lip-turn candidates across thirteen actual sections and inspects three-view overlays. Corners remain uncovered and some turns are hidden; contact geometry and visible photo constraints must be distinguished before fitting. No mesh change.
- Experiment 0093 orders supported sections into unbranched paths with explicit ambiguity rejection. The real lip section forms paths of 30 and 33 points; 81 tests pass. These are cross-section paths, not yet transverse anatomical lip rims.
- Experiment 0092 adds tested mesh sections retaining triangle/barycentric endpoint support. The real 61-segment lip section is reproduced exactly within tolerance; 80 tests pass. Anatomical rim tracing and contact remain unfinished, with no geometry promotion.
- Experiment 0091 inspects the actual lip cross-section and tests vertical-only closure. It still hides the old lower sample and regresses the right profile; both candidates are rejected. Stop two-point attraction trials and establish a surface-curve/contact model for the lip rim.
- Experiment 0090 tests compact local seam closure. Quarter closure does not resolve the visible mouth shape; half closure hides the lower sample in all three frontal/oblique views despite valid triangles. Both candidates are rejected; closure needs explicit lip-rim geometry rather than attraction between existing detector-derived hits.
- Experiment 0089 fits nasal/lip controls on the existing coupled head/cameras. Right profile and point errors decrease, left profile slightly regresses, and actual five-view likeness remains generic. Both immediate and original-source mesh checks are retained; no promotion or repeated identical sweep.
- Experiment 0088 verifies positive transfer of the existing joint camera/head to seam samples excluded from its fit: both oblique fixed-support errors decrease while front stays unchanged. Errors remain material; use this unaccepted coupled configuration as a comparison, without camera or likeness promotion.
- Experiment 0087 removes mesh constraints and fits free seam points: front/left errors remain about 5–6px, and a shared closed-seam point has similar disagreement. Lip closure alone cannot reconcile these fixed-camera observations; shared cross-view alignment needs attention before stronger shape fitting.
- Experiment 0086 finds that seam-sample separation is mostly depth, with no nearby open mesh boundary. A two-ring visible-support search trades frontal accuracy for oblique accuracy at the upper seam and cannot improve the lower sample. No support remapping or mouth closure is promoted.
- Experiment 0085 inspects enlarged mouth photo/clay supports: the photos have a closed seam while the source has an opening, and projected upper/lower seam samples separate by 2.65–5.83px versus detector separation 0.22–0.72px. Resolve opening/configuration and seam support before further lip-volume fitting; anatomy remains unverified.
- Experiment 0084 adds per-row bilateral profile protection to the joint nasal/lip fit. Every tested nonzero step violates a protected row; the retained mesh is unchanged and rejected as an improvement. Two starts did not converge. Repeating this penalty is not the next step; mouth correspondence semantics remain unresolved.
- Experiment 0083 jointly fits ten nasal/lip controls. Frontal/oblique point errors decrease but both actual profile errors increase; the candidate is rejected for promotion after five-view inspection despite valid triangle/visibility checks. Mouth correspondence semantics and explicit profile protection remain unresolved.
- Experiment 0082 fits five symmetric, hash-pinned CC0 central-face controls with the existing unaccepted cameras. Every fitted outline/profile/anchor aggregate decreases and the mesh keeps a 0.925 minimum area ratio, but actual five-view inspection shows only small cheek/chin changes and retains generic eyes, nose, lips and head shape. Candidate remains `UNVERIFIED`; no promotion. 78 tests pass.
- Experiment 0081 prepares fourteen hash-pinned CC0 central-face controls for eye spacing, cheek volume and chin proportions. This is asset-only technical progress, not a fitted likeness; private previews and real fitting remain next.
- Experiment 0080 compares face-restricted existing head controls with fixed versus joint cameras. Outline/anchor tradeoffs remain, profiles barely change, and both candidates fall below the recent 0.5 area-ratio guard. Real five-view results remain generic; no promotion. Stop repeating this four-preset sweep. 78 tests pass.
- Experiment 0079 couples actual-head oblique pose with bounded smooth nasal deformation. It avoids the disconnected free-point camera shift and lowers source-relative facial/nasal fitting errors, but the rendered face remains generic and bounds are active. Candidate unverified; broader identity remains the next focus. 78 tests pass.
- Experiment 0078 rejects global transfer of the nasal y bias to eyes/mouth. Small relative rotations improve free-point consistency but misalign the unchanged head by about 30px in obliques; no standalone camera promotion. Any further use requires joint shape/camera constraints and real all-view checks.
- Experiment 0077 finds nasal midline inconsistency even with free 3D points and no mesh. Alar-only shared vertical biases improve excluded midline prediction, but tip disagreement remains. Diagnose shared view alignment separately from tip correspondence; no camera/shape promotion.
- Experiment 0076 tests total-displacement regularization, then adds an optional graph-Laplacian bending penalty. Source-prior alone retains the crease; bending reduces the visible pinch but retains generic/angular anatomy and view tradeoffs. No promotion. Default behavior unchanged; 78 tests pass.
- Experiment 0075 tests local nasal vertex fitting: bilateral contour and all three alar-view means decrease, but enlarged actual renders show a new nasal-tip crease. Candidate rejected despite valid triangle/visibility checks. Next require smoother shape-preserving deformation; 77 tests pass.
- Experiment 0074 finds that at least 89.4% of the current nasal residual norm lies outside the four-control local linear span, stable across three numerical steps. Stop repeated narrow coefficient sweeps; investigate missing shape support and correspondence/camera errors. This is a local diagnostic, not a proof of global impossibility or visual acceptance.
- Experiment 0073 recomputes the candidate contour during nasal fitting. Side regressions remain; dense versus original annotation-row sampling can disagree even on the same actual silhouette. Real photo/source/candidate comparison is retained privately; no promotion. 77 tests pass.
- Experiment 0072 adds explicit curve support to the tested target fitter and runs real mixed point/curve fitting. Fitted source-arc scores decrease while actual nasal envelopes regress; candidate rejected. Curve distance is not apparent-silhouette accuracy. Full suite: 77 tests.
- Experiment 0071 integrates the public point fitter on real nasal observations and fixes unsupported controls returning arbitrary tiny values. Tip control is now explicitly zero without eligible support. The point-only candidate regresses side evidence and is rejected; 76 tests pass.
- Experiment 0070 adds a tested fixed-camera graphical-target point fitter with explicit eligibility masks and per-point pixel scales. It does not estimate uncertainty or claim visual improvement; real-photo integration and contour checks remain required. Full suite: 75 tests.
- Experiment 0069 triangulates the visible alar pairs without a mesh prior: several-pixel disagreement remains, and recovered offsets are sensitive to assumed 3px input perturbations. Do not convert these detector pairs directly into exact geometry targets; no model/camera promotion.
- Experiment 0068 adds nasal-base vertical control. Frontal alar error decreases, but left-oblique and both nasal profile errors increase; actual five-view comparison does not justify promotion. Original model/cameras stay unchanged.
- Experiment 0067 verifies visible alar support and adds twelve frontal/near-oblique nasal observations. Far-side occluded points are excluded. The fitted candidate still regresses frontal alar and left profile evidence; no promotion. Alar-base vertical support is the next specific question.
- Experiment 0066 prepares six pinned CC0 nasal controls and fits a three-parameter bilateral nose trial. Changes are tiny and left nasal error increases; actual five-view inspection does not support promotion. Frontal/oblique nasal anatomy remains insufficiently constrained.
- Experiment 0065 verifies candidate canthi before/after contour-supported pose fitting, including profile visibility. Same-support camera gains are negligible and actual profiles remain visually unchanged; no promotion. Nose/lip anatomy remains unresolved.
- Experiment 0064 finds four nearby canthus correspondence candidates visible in all three fitting views, with lower projection error and inspected photo/clay crops. Geometry and cameras are unchanged; profile support, pose impact and anatomical accuracy remain unverified.
- Experiment 0063 adds profile arcs to screened pose fitting, restraining the right pose drift and lowering fitted profile errors. Retained anchor errors increase, and actual views remain generic. Both contour and anchors are now training inputs; no camera or likeness acceptance.
- Experiment 0062 applies the three anchor exclusions and reruns fixed-focal pose fitting. The right pose visibly drifts away from the photo and profile MAE worsens to 17.34px despite smaller retained-point error. Candidate rejected; reliable side-view support is still required.
- Experiment 0061 identifies concrete anchor conflicts: the right-profile detector nose target is outside the photo silhouette, and two fitted oblique mouth anchors are self-occluded on the current mesh. Non-destructive rejection guidance and numbered photo/clay crops are retained; original data and cameras stay unchanged.
- Experiment 0060 rejects four fixed-shape focal/pose candidates: some training anchor errors decrease, but both profile checks regress versus the original cameras. Actual bilateral views were inspected; focal is still uncalibrated, and anatomical anchor correspondence is the next audit.
- Experiment 0059 fits four whole-head controls to frontal/oblique outlines and anchors. Outline fitting errors decrease, anchors slightly regress, and bilateral profile errors stay essentially unchanged. Actual five-view comparison still lacks likeness; the candidate is unverified and not promoted.
- Experiment 0058 adds four pinned CC0 whole-head shape assets and inspects actual fixed-camera scope previews. They affect skull/face/jaw proportions but barely change the nose/lip profile; subject fitting and visual improvement remain unverified. Preparation supports an explicit reviewed target lock.
- Experiment 0057 rejects authored lip-height/position fitting: mouth-point error decreases but both side profiles regress. Additional CC0 target assets are separately locked; broader face-shape coverage is the next investigation, not repeated lip-only adjustments.
- Experiment 0056 fits the authored mouth-volume assets to actual multi-view inputs. Small fitting-error decreases and valid local triangle checks do not establish visible likeness; the candidate stays unverified. Lip height/position remains a separate next question.
- Experiment 0055 prepares six hash-pinned CC0 mouth/philtrum shape targets with independent sparse-data parsing and exact source-ID mapping. Generic previews were inspected; fitting these targets to the subject is next. No identity acceptance; 71 tests pass.
- Experiment 0054 tests six smooth lip modes: right fitting error improves only with left regression; per-point left protection yields an effectively unchanged mesh. Neither candidate is promoted. An anatomically structured shape basis is the next avenue, not larger ad hoc lip updates.
- Experiment 0053 lowers bilateral local lip fitting error while preserving protected projections, but actual clay views show unacceptable lip protrusions. Candidate rejected for visual promotion; further identical vertexwise iterations are not the next step.
- Experiment 0052 identifies scanline correspondence switching from chin to neck and adds a tested ordered-curve distance diagnostic. Translation-only candidates still regress chin/anchor alignment and are rejected; no camera promotion. Full suite: 69 tests.
- Experiment 0051 reduces the right-profile fitting MAE from 8.03 to 7.12 px while preserving frontal vertex projections and all 426 sampled left-profile rows. Actual photo overlays still show nose/lip defects; the candidate remains unverified and is not promoted.
- Experiment 0050 adds occlusion-preserving component filtering to surface lifting. On the actual combined head it explicitly rejects 18 eye-helper hits as body observations, including all five previously audited eye mismatches. Anatomical correctness remains unverified; 67 tests pass.
- Experiment 0049 adds an explicit, non-default CC0 eye-helper preparation option, verified on the pinned asset and rendered in all five views. Generic eye surfaces now have a local experimental output; subject-specific eyes and likeness remain unverified. Full suite: 66 tests.
- Experiment 0048 confirms substantial cross-view drift in clay-derived bridge/nose correspondences on the exact same unchanged head. These mappings remain unverified and must not be treated as anatomical truth for stronger deformation.
- Experiment 0047 rejects a dense pose-only candidate: detector residuals decrease but manual-anchor alignment worsens in all three fitted views. Cameras are not promoted; central anatomical correspondence support must be resolved before stronger deformation.
- Experiment 0046 reruns dense fitting with screened eye support. On identical corrected evaluation support, held p95 is unchanged versus 0044 (23.0857 px); no clear visual improvement or baseline promotion. The largest remaining held residuals include exactly frozen central points, requiring a correspondence/camera diagnosis before relaxing profile protection.
- Latest audit 0045 identifies internal eye-surface hits masquerading as eyelid correspondences. A five-point, correspondence-only rim proposal reduces large oblique errors without changing the mesh. It remains `UNVERIFIED`; unrestricted anatomical use of raw clay hits is rejected. See the experiment before repeating dense deformation.
- Latest experiment 0044: dense triangle-correspondence fitting runs on the actual five-photo subject; held detector-point p95 decreases from 26.56 to 23.49 px, but visual likeness remains unverified and left profile MAE slightly worsens. No baseline promotion. Full suite: 65 tests.
- Product/technical research: complete enough to select an architecture.
- Camera projection baseline: implemented and covered by deterministic synthetic tests.
- Weight-independent perspective landmark solver: implemented; first real-photo held-out camera check is `REJECT` (39.35 px p95). See experiment 0005. Install `.[geometry]` for this optional solver.
- Commercial VGGT adapter: local output contract and asset lock implemented; real gated checkpoint execution is `UNVERIFIED`.
- Input rights and capture validation: implemented; missing consent, provenance, license, file hash, view coverage, resolution, or clarity evidence is `REJECT`.
- Side-profile contour fitting: deterministic jaw/chin/neck slice is `TECHNICAL_CHECK_PASSED`; real-photo improvement is `UNVERIFIED`.
- Real-photo face-patch diagnostics: OBJ export and CPU depth/texture rendering work; these are not full heads and use cameras that still fail validation. Experiments 0007–0008 document visible limitations.
- Dense camera diagnostic: 60 held-out points yield 10.44 px p95, still `REJECT`; see experiment 0009. No full-head or side-profile quality acceptance.
- Convergence audit: extending to 60 iterations yields 9.73 px, still `REJECT`; experiment 0010 includes a shape-independent epipolar check and inspected photo overlays.
- Shape-independent calibrated initialization: implemented and synthetically tested; real-photo candidate rejected (experiment 0011). Positive depth does not imply correct calibration.
- Nonlinear pair-pose refinement: implemented; fixed-focal pair errors improve, but the prior-free three-view held-out reprojection remains `REJECT` at 11.80 px (experiment 0012).
- Correspondence audit: no independent three-view texture tracks found in the bounded masked-SIFT check; manual physical-landmark verification is next (experiment 0013). This does not establish that the photos are unusable.
- Independent visual reading: six anatomical anchors checked against fixed cameras; p95 8.23 px with material reading uncertainty, still `UNVERIFIED` (experiment 0014).
- Optional XFeat local extraction: pinned source/weight/consent checks implemented; sparse three-view track candidate remains `REJECT` (experiment 0015). No VGGT checkpoint substitution.
- XFeat fine matching: one strict three-view cycle; symmetric endpoint refinement gives zero. Insufficient support for camera acceptance (experiment 0016).
- LighterGlue local matcher: locked checkpoint and Kornia 0.8.1 loader implemented. A frozen 40-train/11-held-track joint camera fit yields 7.5456 px held-out p95, still `REJECT` (experiment 0017).
- Robust camera initialization: explicit training-only consensus, duplicate/intrinsic/low-parallax guards and synthetic outlier tests implemented; these do not diagnose the real-photo failure.
- DA3-BASE: pinned local CPU inference and depth/camera conversion implemented; all five photos executed. Same-track joint refinement yields 7.5485 px held-out p95, still `REJECT`; no measured final-alignment improvement over the previous initializer (experiment 0018). Current full suite: 43 tests.
- Correspondence localization: all eleven held tracks visually inspected; a bounded bidirectional translation tracker retains no held-out tracks and is not adopted (experiment 0019). No validation points were removed to obtain a pass.
- Local affine matching also supplies zero fully consistent three-view replacement tracks (experiment 0020). High patch similarity alone is not treated as physical point agreement.
- Geometry reconstruction: experimental anatomical template fitting and mesh export implemented; subject likeness and production acceptance remain incomplete.
- Texture fusion: architecture selected; implementation not yet started.
- KeenTools-level visual parity: **UNVERIFIED**. No claim is made until the complete acceptance suite passes.

## Quick start

```powershell
cd C:\workspace\headfoundry
C:\Python313\python.exe -m pip install -e .
C:\Python313\python.exe -m unittest discover -s tests -v
C:\Python313\python.exe -m headfoundry.camera
C:\Python313\python.exe -m headfoundry.vggt tests\fixtures\vggt_camera_point_fixture.json
C:\Python313\python.exe -m headfoundry.profile examples\profile_fixture.json --svg docs\experiment-0003-profile.svg
C:\Python313\python.exe -m headfoundry.manifest path\to\run-manifest.json
C:\Python313\python.exe -m headfoundry.quality examples\quality_manifest.json
```

The VGGT fixture check must report `TECHNICAL_CHECK_PASSED`; this proves the adapter and matrix conventions, not the real checkpoint or visual quality. `examples/run-manifest.template.json` documents the required asset fields and intentionally fails until its placeholders are replaced with actual files, hashes, rights, and consent. Manifests may be limited to `local_head_reconstruction_validation`; every input's `allowed_uses` must match the declared purpose, so local consent cannot be expanded to commercial use. The example quality manifest intentionally fails later-stage gates.

## Commercial checkpoint installation

Only `facebook/VGGT-1B-Commercial` with license id `vggt-aup-license` is accepted. The original `facebook/VGGT-1B` is rejected even if it is locally available.

1. An authorized person reviews and accepts the gated model terms at [facebook/VGGT-1B-Commercial](https://huggingface.co/facebook/VGGT-1B-Commercial). HeadFoundry does not automate acceptance.
2. Download `model.safetensors` through the authenticated Hugging Face web UI or CLI into `assets/private/VGGT-1B-Commercial/`. This directory is git-ignored.
3. Compute its SHA-256, copy `examples/run-manifest.template.json`, and record the exact path, digest, accepting person/date, license id, AUP review, and non-military use declaration.
4. Run `python -m headfoundry.manifest <manifest>`. Any missing or mismatched field is `REJECT`; there is no fallback checkpoint.

The separate free-commercial DA3-BASE candidate has its own locked local runner,
not a VGGT fallback. See [installation and measured limits](docs/experiment-0018-da3-base.md#reproduction).

## FLAME 2023 Open installation

Only the official `FLAME 2023 Open` archive is eligible. Its shape model is
CC-BY-4.0 and permits commercial use with attribution and the published use
restrictions; older FLAME releases and the separate texture model are not
eligible. Sign in at the [official FLAME download page](https://download.is.tue.mpg.de/download.php?domain=flame&sfile=FLAME2023Open.zip)
and place `FLAME2023Open.zip` under
`assets/private/FLAME-2023-Open/`. Do not substitute or rename an older model.
Convert and lock the private asset without executing unrestricted pickle code:

```powershell
C:\Python313\python.exe tools\prepare_flame_open.py `
  assets\private\FLAME-2023-Open\FLAME2023Open.zip `
  assets\private\FLAME-2023-Open\converted-v1 `
  --reviewed-by "REPLACE_WITH_REVIEWER" `
  --reviewed-at "YYYY-MM-DD"
```

The generated lock binds the source ZIP, official pickle and safe NPZ. Complete
its reviewer fields before loading it. Asset installation is not evidence of
subject likeness; experiment 0143 rejects the tested identity candidates.

## Blender clay diagnostic

Blender 5.2 LTS can turn an existing OBJ into a reproducible five-view neutral
clay review without changing its geometry:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background --python tools\blender_clay.py -- `
  path\to\head.obj path\to\new-output-directory
```

The importer applies the current HeadFoundry OBJ y-down/z-back convention. The
non-overwriting output contains `diagnostic.blend`, five PNG views and a
hash-bound `report.json`. Its status is always `UNVERIFIED`: a Blender render is
diagnostic evidence, not camera, identity or likeness acceptance.

For exact fixed-camera photo overlays, supply the five-view camera NPZ and a
directory containing `front`, `left30`, `left90`, `right30`, and `right90` PNGs:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background --python tools\blender_camera_diagnostic.py -- `
  path\to\head.obj path\to\cameras.npz path\to\photos path\to\new-output
```

The command fails before rendering unless Blender's independent projection
replay agrees within 0.05 px. Photographs and generated scenes must remain in
ignored private storage.

## Project documents

- `docs/PRD.md`: authoritative product requirements and acceptance contract.
- `docs/PRODUCT.md`: authoritative current product status, verification and next gate.
- `docs/report-source.md`: canonical technical research report.
- `docs/claim-source-ledger.md`: claim-to-source audit trail.
- `docs/adr/0001-quality-first-reconstruction.md`: architecture decision.
- `docs/experiment-0001-camera-baseline.md`: first falsifiable experiment record.
- `docs/experiment-0002-commercial-vggt-adapter.md`: commercial checkpoint adapter and deterministic camera-gate record.
- `docs/experiment-0003-profile-contour.md`: bounded side-profile contour experiment and next real-image gate.
- `docs/experiment-0017-lighterglue-camera.md`: locked local matching, whole-track validation, robust initialization guards and rejected joint camera fit.
- `docs/experiment-0018-da3-base.md`: explicit free-commercial local camera/depth candidate, frozen observations and rejected refinement.

## Legal boundary

KeenTools Cloud is used only as a publicly documented product-quality reference. Its service, private sessions, generated outputs, and implementation are not used as training material, reverse-engineering inputs, or automated competitive benchmarks.
# Latest experimental geometry (2026-09-08)

[Experiment 0043](docs/experiment-0043-clay-surface-correspondence.md) establishes
an experimental detector-to-clay correspondence route: 464 exact visible surface
hits, four explicit misses. Projection correctness is tested, anatomical accuracy
is not accepted. Current suite: 64 tests.

[Experiment 0042](docs/experiment-0042-clay-normal-diagnostic.md) adds optional
smooth-normal clay inspection alongside the unchanged flat default. Five-view
depth/visibility buffers are exact; this changes lighting, not geometry or
likeness. Current suite: 63 tests.

[Experiment 0041](docs/experiment-0041-planar-neck-termination.md) removes the
irregular shoulder crop with exact shared-edge plane clipping, preserving
retained facial coordinates. The short neck remains open and generic; this is
not likeness acceptance. Current suite: 62 tests.

[Experiment 0040](docs/experiment-0040-cheek-protection-support.md) confirms that
an oversized protected rectangle froze oblique cheek constraints. A bounded
feature-ring experiment reduces those fitting errors with frontal projection
and central-profile regression checks intact; likeness is still unverified.

[Experiment 0039](docs/experiment-0039-photo-oblique-boundaries.md) records
original-photo oblique boundary readings independent of model projection.
The resulting bounded geometry change is negligible and not adopted; protected
cheek support and camera uncertainty require review before further fitting.

[Experiment 0038](docs/experiment-0038-oblique-jaw-rejection.md) rejects a
far-side detector-oval fit: those points are not the visible oblique silhouette.
No new geometry baseline is adopted. Independent boundary evidence is needed
before repeating oblique fitting; the full reconstruction remains incomplete.

[Experiment 0037](docs/experiment-0037-lower-face-outline.md) fits lower cheek/jaw
width with protected facial features. A rear-neck contour-confound trial was
rejected; the corrected face-ROI experiment has inspected five-view evidence but
no accepted likeness. Current suite: 60 tests.

[Experiment 0036](docs/experiment-0036-continuous-profile.md) fits continuous
projected edge positions with perspective-correct weights. Both profile fitting
residuals decrease while frontal vertex projections stay fixed; full likeness
remains unverified. Current suite: 60 tests.

[Experiment 0035](docs/experiment-0035-frontal-protected-profile.md) adds local
profile depth fitting that preserves frontal vertex projections. Fixed-camera
five-view evidence exists; profile fitting residuals decrease but likeness is
still unverified. Current suite: 58 tests.

[Experiment 0034](docs/experiment-0034-anatomical-template-pose.md) places the
unchanged anatomical template in all five photos and provides actual clay and
overlay comparisons. Pose is experimental, shape is still generic; no likeness
or camera acceptance. Current suite: 56 tests.

[Experiment 0033](docs/experiment-0033-cc0-head-prior.md) installs a pinned CC0
MakeHuman head/neck template without its AGPL program code. It provides a coherent
anatomical starting mesh; it is **not yet fitted to the subject**.

[Experiment 0032](docs/experiment-0032-photo-profile-step.md) directly applies
approximate photo-profile constraints to the shared mesh and provides fixed-camera
before/after evidence. Coarse head shape remains visibly rejected.

[Experiment 0031](docs/experiment-0031-shared-radial-shell.md) creates a single
closed experimental shell and original-photo comparison with inferred regions
marked. The visible shape remains rejected; direct photo-contour fitting is pending.

[Experiment 0030](docs/experiment-0030-affine-depth.md) tests a bounded depth
offset. Held error changes only marginally and the active camera bound remains;
the candidate is rejected, with experimental shared-surface work next.

[Experiment 0029](docs/experiment-0029-active-bound.md) identifies opposing depth
and pixel gradients at the active camera bound. Parameters and held error are
unchanged; the diagnostic does not justify widening constraints or acceptance.

[Experiment 0028](docs/experiment-0028-joint-pixel-depth.md) adds joint image/depth
constraints. Held projection reaches 8.82 px, but a bound is active and depth
consistency slightly regresses. The candidate is not accepted.

[Experiment 0027](docs/experiment-0027-depth-camera-registration.md) adds bounded
joint depth/camera registration. Held error drops from 25.76 to 11.66 px, still
failing the gate; profiles and complete-head quality remain unverified.

[Experiment 0026](docs/experiment-0026-ray-camera.md) tests DA3's alternate ray
camera path with identical depth arrays. Unrefined prediction errors decrease,
but the camera gate still fails; no accepted head or quality parity is claimed.

[Experiment 0025](docs/experiment-0025-depth-sampling.md) provides a fixed-frame
nearest/bilinear comparison. Large seams persist; substantial cross-view depth
conflicts remain. Sampling changes do not establish likeness improvement.

[Experiment 0024](docs/experiment-0024-free-space-fusion.md) retains free-space
evidence during fusion. Boundary count decreases, but visual seams persist;
the result is still rejected as a usable head.

[Experiment 0023](docs/experiment-0023-projective-fusion.md) implements and tests
shared depth fusion. The real-subject candidate is rejected for visible cracks
and noise; it does not establish side-profile improvement.

[Experiment 0022](docs/experiment-0022-common-frame-orbit.md) adds a common-frame
orbit and OBJ union. Rotation exposes substantial overlapping-sheet errors;
this is an inspection artifact, not a fused/accepted head.

User-authorized, unaccepted depth-surface exports now exist locally. See
[experiment 0021](docs/experiment-0021-observed-depth-surfaces.md) for the actual
five-view clay comparison, limitations and counts. These are separate open
surfaces, not a complete head; camera acceptance and visual quality remain unmet.
