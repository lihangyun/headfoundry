# HeadFoundry product status

Last updated: 2026-09-23 after experiment 0159.

## What exists

- A Python package under `src/headfoundry` with fail-closed rights/input manifests, camera conventions and gates, commercial-checkpoint adapters, depth/camera diagnostics, surface fitting, clipping, rasterization and profile diagnostics.
- Deterministic fixtures and regression tests under `tests`, plus pinned asset identities and example manifests under `examples`.
- A clean-room research trail in `docs`, including the governing ADR, claim/source ledger and numbered experiments.
- Experimental OBJ/head rendering on local authorized photographs. Private inputs and identity-derived artifacts stay under ignored local paths.
- GitHub repository: `https://github.com/lihangyun/headfoundry.git`, branch `main`.

## Current result

Experiment 0159 tests the classical-stereo depth hypothesis. The two
triangulated front/30-degree clouds contain 2,908/3,368 samples but only 443
cross-pair points agree within 0.03 model units. Their fusion covers only 7/17
and 7/16 reviewed pure-profile rows; covered-row errors are 34.21/21.41 px.
Local overlays show missing mouth/chin support. Execution is
`TECHNICAL_CHECK_PASSED`; this subject geometry is `REJECT`. The next gate uses
pure-profile contours directly as fixed-camera shape evidence and requires
visible five-view improvement before promotion.

Experiment 0158 establishes a model-free dense-photo route. Fixed front/left-30
and front/right-30 cameras rectify successfully; 11-pixel semi-global matching
reaches 4.06/4.64 px median disparity error on reviewed central correspondences
with 50.2%/51.7% valid masked-face coverage. Correspondence feasibility is
`TECHNICAL_CHECK_PASSED`; depth and geometry remain `UNVERIFIED` pending
triangulation, pair consistency and unused-profile validation.

Experiment 0157 maps all 82 paired controls onto the current closed mesh. A
profile-weighted fit safely improves every aggregate outline/profile metric,
but untouched profile rows reject it: left held error worsens from 4.247 to
4.643 px and right from 4.387 to 4.526 px. Exact Blender overlays show no
confident identity gain. Mapping and solver execution are
`TECHNICAL_CHECK_PASSED`; subject, visual and default promotion are `REJECT`.
Training a decoder on this same rejected source manifold is not justified.

Experiment 0156 converts the locked target basis into 82 paired neutral
controls and generates 256 deterministic synthetic identities. Maximum
displacement is 0.1914, minimum area ratio is 0.4117 and no triangles reverse.
A fixed 12-sample front/profile contact sheet shows coherent heads with modest
diversity. Generation and mesh safety are `TECHNICAL_CHECK_PASSED`; coverage,
realism and subject quality remain `UNVERIFIED`.

Experiment 0155 expands the same pinned official CC0 MakeHuman source from 92
selected assets to 348 reviewed face/head targets. Every target's explicit CC0
header and SHA-256 are verified, then mapped to one 4,459-vertex head topology.
Rights, lock and conversion are `TECHNICAL_CHECK_PASSED`; identity quality is
`UNVERIFIED`. This is the deterministic source basis for a controlled synthetic
nonlinear identity prior, not a subject-quality claim.

Experiment 0154 tests eight coherent macro identity modes, first shared and
then independently on the two visible hemispheres. Both optimizers converge,
but every nonzero step trades right-side improvement for left train/held
regression; removing symmetry coupling does not resolve the conflict. The path
is `TECHNICAL_CHECK_PASSED`, while both representations and all visual/default
promotion are `REJECT`. Hand-authored scalar identity modes are exhausted.

Experiment 0153 replaces the broad mouth field with six anatomical layers. A
0.20-scale experimental candidate improves both fitted profiles, the combined
held score and both oblique outlines; maximum movement is 0.00371, minimum area
ratio is 0.953 and no triangles reverse. The path is
`TECHNICAL_CHECK_PASSED` and the balanced numerical result is
`PARTIAL_SUCCESS`. Exact Blender overlays show no confidently visible identity
gain, so visual/default promotion is `REJECT`. Small local depth fields on the
current generic mesh have reached diminishing returns.

Experiment 0152 gives the two visible facial hemispheres separate smooth
lower-face capacity with fixed cameras and same-side oblique transfer. The
smallest nonzero step improves both fitted profile subsets, the left held rows
and both oblique outlines, but right held error immediately worsens from 4.594
to 4.608 px and degrades thereafter. Execution is `TECHNICAL_CHECK_PASSED`;
every nonzero geometry is `REJECT`. Side coupling is not the missing capacity;
the next basis must resolve distinct upper-lip, seam, lower-lip, labiomental and
chin anatomy.

Experiment 0151 confirms that experiment 0150's tiny gain is not caused by an
apparent-contour support jump. All sampled right-profile nose, mouth and chin
rows retain a shared baseline-edge vertex, with no more than 0.000130
model-unit support motion. This read-only check is `TECHNICAL_CHECK_PASSED`,
but it establishes numerical continuity rather than anatomical identity. The
next shape test separates the two visible hemispheres and requires same-side
oblique transfer under the existing protections.

Experiment 0150 fits and line-scans a tiny physical right-profile camera
perturbation under independent near-eye, subnasale, nose, chin, cheirality,
focal and rigid-matrix protection. A feasible scale exists, but held-mouth
error falls only 0.071 px (6.504 to 6.433, about 1.1%) with rotations below
0.012 degrees. The diagnostic is `TECHNICAL_CHECK_PASSED`, the protected
nonzero direction is `PARTIAL_SUCCESS`, and camera promotion is `REJECT`.
Camera error cannot explain the visible lower-face deficit; retain the 0132
cameras and move to correspondence/anatomical shape capacity.

Experiment 0149 separates one shared neutral lower-face step from three bounded
per-profile expression nuisance modes while freezing every camera. The solver
converges, but the right transfer mean still worsens from 4.594 to 5.320 px and
the right adjusted mesh reverses 536 triangle normals. Execution is
`TECHNICAL_CHECK_PASSED`; neutral and adjusted candidates are `REJECT`, and the
expression explanation remains `UNVERIFIED`. The next discriminating test is a
small physical right-profile camera perturbation, accepted only if independent
eye, nose, ear and chin evidence on the unchanged mesh is preserved.

Experiment 0148 shows that the rejected right-side transfer conflict spans
three consecutive subnasal/lip samples rather than one obvious bad point; two
lower-chin samples improve, and four of five left transfer samples improve.
Read-only replay is `TECHNICAL_CHECK_PASSED`, geometry remains `REJECT`, and the
cause remains `UNVERIFIED`. The next architecture must treat small per-view
mouth expression/pose as a nuisance variable separate from neutral identity,
not encode one photograph's mouth state as asymmetric neutral geometry.

Experiment 0147 tests a structured bilateral lower-face spline. At the first
nonzero scale, both fitted profile subsets improve and left transfer improves,
but right transfer worsens from 4.594 to 4.607 px and degrades monotonically as
the step grows. Nose, eyes, frontal/oblique outlines and topology remain safe.
The path is `TECHNICAL_CHECK_PASSED`, every nonzero geometry is `REJECT`, and
zero is retained. This is a bilateral evidence conflict, not permission to
weaken the transfer guard; right-profile correspondence/camera uncertainty is
the next diagnostic.

Experiment 0146 replays the fixed 0132 mesh/cameras on manually partitioned
existing profile observations. Nose error is already lowest at 0.84/3.10 px;
mouth remains 3.44/5.76 px and chin/jaw 5.12/4.22 px, while the right upper
bridge is a separate 8.46 px discrepancy. Hair, cranium and cut-neck boundaries
are excluded. The audit is `TECHNICAL_CHECK_PASSED`, not independent evidence or
a promoted result. The next shape family must couple mouth with chin/jaw while
protecting nose, eyes, frontal/oblique evidence and topology.

Experiment 0145 reproduces all five fixed project cameras in Blender with less
than 0.00013 px maximum independent vertex-projection disagreement. This path is
`TECHNICAL_CHECK_PASSED`. Actual semi-transparent overlays reject a whole-head
alignment claim: the frontal envelope is broadly coincident, but the two pure
profiles expose major disagreement in cranial depth, posterior skull/neck and
the artificial cut region. Previous 3–5 px selected facial-row scores are local,
not full-head acceptance. No camera or geometry is promoted.

Experiment 0144 adds a reproducible Blender 5.2.1 LTS clay-review path. It
imports the current OBJ convention, generates five fixed orthographic views,
saves a reopenable scene and records the source hash without changing geometry.
The path is `TECHNICAL_CHECK_PASSED`. Actual experiment-0132 renders remain
visibly generic with unresolved lips and incomplete eyes, so identity stays
`UNVERIFIED` and no camera, geometry, texture or parity gate is promoted.

Experiments 0142–0143 establish the fail-closed local contract for the official
CC-BY-4.0 `FLAME 2023 Open` identity model. A pure-NumPy adapter validates the
exact model identity, source, license, attribution/review records, upstream and
converted hashes, 300-dimensional shape basis and triangle topology. A
deterministic fixture, negative cases and the real 5,023-vertex model pass, so
the asset/conversion adapter is `TECHNICAL_CHECK_PASSED`. Identity fitting and
topology transfer remain visibly generic: the best transfer reports bilateral
profile means of 32.22/30.42 px, far worse than the current 0132 result at about
3.62/4.92 px. All FLAME identity/default promotion is `REJECT`; KeenTools-level
quality remains `UNVERIFIED`. Old FLAME releases and the separate non-commercial
texture model remain prohibited.

Experiments 0140–0141 exhaust the tested front-camera-ray central-depth family
under the experiment-0132 cameras. A direct 20,362-vertex surface direction can
retain all guards only at 0.000300 maximum movement and is visually
imperceptible; a 30-center smoothed approximation selects zero. A separately
optimized 30-field RBF basis also selects zero after its constrained solver
reaches the iteration limit. Its first nonzero replay step improves both profile
means slightly but worsens one oblique outline and the right reviewed-material
mean. The deterministic paths are `TECHNICAL_CHECK_PASSED`; all geometry,
identity and default promotion is `REJECT`. More local ray fields or weaker
guards are not a supported next step.

Experiment 0139 transfers the two closed CC0 MakeHuman eye components into the
current experimental head while preserving every head vertex and camera exactly.
They are visible in all five views and remove the conspicuous empty eye sockets.
The asset/topology path is `TECHNICAL_CHECK_PASSED` and the actual visual result
is `PARTIAL_SUCCESS` for completeness, but `REJECT` for identity/default
promotion: the eyes are generic, disconnected and have no subject iris, gaze,
cornea, eyelid-contact fit or texture.

Experiment 0138 adds the reviewed profile material points to the six-field
central-depth objective. A guarded line scan finds a safe 0.003659-unit step,
improving the left material mean from 9.0087 to 8.6399px while the right is
effectively unchanged. The optimizer reports failure and native profile crops
are visually indistinguishable, so numerical replay is
`TECHNICAL_CHECK_PASSED` but candidate promotion is `REJECT`. The compact
six-field basis is exhausted as a visible identity route.

Experiment 0137 tests the 0135 profile-camera movement on a separately defined
set of front-lifted, visually reviewed near-eye and lip/subnasale material
points. The 0.76 silhouette-selected scale worsens left/right material means
from 9.0087/10.2408 px to 9.1528/10.8358 px, and zero is the best of the full
101-step direction scan. The fixed-point replay is `TECHNICAL_CHECK_PASSED`;
the profile detections and current shape remain provisional, so the result is
not camera truth. It rejects promotion of 0135 as a generally better camera and
keeps its `PARTIAL_SUCCESS` limited to the same-photo contour diagnostic.

Experiments 0133–0136 resolve four competing explanations for the remaining
central-face error. Simple mouth-depth smoothing makes both dense profile splits
worse and is rejected. Three in-domain MediaPipe views provide a stable relative
depth consensus, but every guarded application to the current head selects zero
because left/right profiles disagree. A separate dense-row camera refinement
retains a nonzero 0.76 scale and improves legacy sparse means plus withheld-row
dense means/p95; matrix, focal, center and cheirality checks pass. Actual visual
change is small and the evidence is same-photo, so the camera remains
`PARTIAL_SUCCESS` diagnostically and `REJECT` for promotion.

An independent Apache-2.0 MediaPipe canonical face patch removes the old
surface-attachment assumption. It produces a coherent coarse facial patch, but
right-profile dense error is 10.58 px versus 4.65 px on the left, and oblique
all-point p95 remains 19–22 px. The patch is not a full head and is rejected for
integration. These results point to unresolved right-profile camera/
correspondence semantics, not permission to add stronger deformations. Camera,
identity, texture and KeenTools-level parity remain `UNVERIFIED`.

Experiment 0132 fits six compact subject-derived nose/lip depth fields with the
experiment-0131 cameras and outer shape frozen. Corrected left/right profile
means improve from 4.342488/5.776622 px to 3.623644/4.923311 px; oblique
central-point means also improve, while all eye and outer-outline diagnostics
are numerically preserved. Maximum movement is 0.029824, minimum relative
triangle area is 0.796018 and there are no normal reversals. Enlarged bilateral
renders show a meaningful contour movement, but the lips remain angular and
generic and one coefficient reaches its bound. The route is
`TECHNICAL_CHECK_PASSED`, the candidate is `PARTIAL_SUCCESS`, and default
promotion is `REJECT`. All measurements and visual comparisons use fitting
evidence; full identity and KeenTools-level parity remain `UNVERIFIED`.

Experiment 0131 fits a broader nine-direction CC0 identity basis while strictly
protecting every oblique eye anchor, both corrected profile groups and mesh
safety. All four fitted outline means and both profile means improve; the eight
eye errors remain unchanged to numerical precision, maximum displacement is
0.021726, minimum relative triangle area is 0.727712 and there are no relative
normal reversals. Actual five-view inspection confirms a modest change in
forehead, cheek and jaw proportions, but the nose, eyelids and lips remain
generic and the provisional non-eye point means regress slightly. Technical
execution is `TECHNICAL_CHECK_PASSED`, the candidate is `PARTIAL_SUCCESS` as
protected outer-shape evidence, and default promotion is `REJECT`. The fitting
views are not held-out validation and KeenTools-level parity remains
`UNVERIFIED`.

Experiment 0130 exactly transfers one locked CC0 lower-lip target through the current subdivision and closed patch. The boundary-only candidate preserves every eye/profile/mesh safeguard and improves both profile means at full authored strength, but actual five-view change is too small to recover identity. Direct interior transfer produces more amplitude only by reversing triangles and worsening the right profile; simple graph smoothing fails too. Transfer verification `TECHNICAL_CHECK_PASSED`, safe numerical result `PARTIAL_SUCCESS`, all visual promotion `REJECT`. Stop isolated generic lip-target tuning.

Experiment 0129 tests one localized lower-lip relief scalar with the 0128 mesh and cameras fixed. Only zero preserves every 0128 diagnostic. A visually clear -0.008 trial keeps all eye errors unchanged and remains better than the pre-0128 source on both profiles, but slightly regresses the 0128 right profile and still looks like a generic bump. `TECHNICAL_CHECK_PASSED` as a bounded sensitivity test, `REJECT` for geometry promotion. Do not spend more iterations tuning this scalar; the next shape direction must represent actual lip anatomy and bilateral evidence.

Experiment 0128 scales the failed per-anchor direction to a strictly feasible nonzero candidate. All eight protected eye errors and both bilateral profile means improve, while minimum area ratio remains 0.957 with no relative normal reversals. Actual five-view appearance changes only slightly and retains generic identity/flat lower lip. `PARTIAL_SUCCESS` for constrained numerical evidence, `REJECT` for baseline promotion. Further progress requires a more expressive identity shape direction, not weaker protection.

Experiments 0126–0127 retain the reconnected patch's geometry stability during joint fitting. The unconstrained candidate regresses left-eye alignment; the mean-protected solve reports failure and has negative left-eye slack. A single eye also worsens from 5.42 to 10.30 px while its view mean nearly stays fixed. Neither candidate is promoted. Per-anchor evidence and solver termination must remain explicit; aggregate protection is insufficient.

Experiment 0125 verifies a concrete numerical gain: identical deformation on the reconnected patch yields minimum area ratio 0.884 rather than 0.233, with zero tested sub-half-area triangles or relative normal reversals. The optional diagonal helper is tested, while defaults stay unchanged. Actual five-view identity remains generic and one profile slightly regresses; no likeness promotion. 99 tests pass.

Experiment 0124 identifies very thin source patch triangles behind the worst recent area-ratio failures. An internal-diagonal reconnection trial preserves UV vertices/boundary and substantially improves planar triangle quality. A recomputed depth surface is `UNVERIFIED`, pending actual rendering and repeated deformation safety checks. This is numerical preparation, not likeness improvement.

Experiment 0123 executes a coupled actual-surface/pose candidate. It avoids the previous large eye shift but still regresses left eye and right profile evidence and fails the area-ratio guard (0.215 minimum). No promotion. Compact depth fields are not yet a shape-safe identity solution; keep surface and view protection rather than expanding bounds.

Experiment 0122 confirms that the free-point camera candidate misaligns the actual unchanged head: eye errors rise to 25.24/23.47 px with supports still visible. No standalone camera transfer is permitted. Different view-specific chin hits do not by themselves prove contour semantics; retain that uncertainty and require actual shared-surface constraints in subsequent coupled fitting.

Experiment 0121's eye/nose-trained physical rotation correction transfers to excluded mouth observations (1.92/1.09 px), but eye and chin regressions prevent promotion. The free-point depths shift materially, so no improvement of the unchanged head is implied. Review actual eye support and chin contour semantics before coupled shape/camera fitting; no camera default changes.

Experiment 0120 extends the current-camera free-ray diagnosis to eyes, nose, mouth and chin. Their signed vertical residuals differ materially, including opposite signs at chin versus nose/mouth. A uniform mouth-derived image shift is not an appropriate whole-face correction. No reconstruction candidate is promoted; physical relative pose and landmark-specific biases still need separation.

Experiment 0119 adds two interior-lip cross-view supports. The fit retains a flat lower lip and worsens both profiles. Removing the mesh restriction still leaves mostly vertical oblique residuals of 4–8 px along fixed frontal rays. This rejects forcing these provisional correspondences into depth-only geometry; wider shape freedom alone is not supported by the evidence. Candidate promotion is `REJECT`.

Experiment 0118 tests a pose-only explanation with the actual fixed mesh: fit profile rotations on non-mouth rows and evaluate excluded mouth rows. Both excluded regions regress, so the cameras are rejected for promotion despite smaller training errors. This does not certify the existing cameras or isolate shape as the sole cause; anatomical cross-view support remains necessary.

Experiment 0117 identifies and corrects misplaced profile observations but the controlled re-fit still flattens the lower lip and produces no meaningful visual improvement. Candidate promotion is `REJECT`. A lower-lip perturbation increases the photo-only objective even without the prior, indicating a constraint/shape-support issue rather than solely excessive regularization. Original sparse profile metrics are not independent or accurate photo-boundary ground truth. Shared camera/correspondence support and broader shape constraints take priority over another local three-control sweep.

Experiment 0116 confirms a geometric boundary discontinuity and tests a local tangent collar. Maximum seam angle falls from 102.78 to 19.03 degrees, but actual all-view identity is unchanged, the lower lip remains flat, relative triangle changes are large and the right profile slightly regresses. Candidate `REJECT`; no baseline promotion. Boundary-angle optimization alone cannot solve the missing lip relief or broader likeness.

Experiments 0114–0115 produce a local closed-mouth replacement with an exactly shared boundary and unchanged retained head geometry. Geometry-aware interpolation substantially reduces artificial striping seen in the first patch. The actual mouth is closed, but the profile-only fit flattens the lower lip and worsens the left profile; full identity is still generic. Both candidates remain `REJECT` for promotion. This neutral patch removes the old cavity and does not support expressions or teeth.

Experiment 0113 tests a monotone vertical gap map directly on the smooth surface with fresh sampled contact heights. Actual frontal gaps narrow, but the side shape remains wrong and both profile means worsen. Half strength violates the triangle-area guard; stronger closure introduces corner-region intersections. Both candidates are `REJECT`. All 94 tests pass, but natural closure and recognizable identity remain unmet. Do not amplify this field or treat its continuous monotonicity as a collision certificate for the output mesh.

Experiments 0111–0112 reject a separately locked mouthClose target: sampled lip intersections occur even on the untouched base. A new independent Catmull-Clark helper produces actual smooth-surface meshes and five-view comparisons. Faceting decreases, but the mouth remains open/generic and the left profile worsens, so no refined mesh is promoted. The next shape fit must evaluate the smooth surface and re-establish its visible/contact support; post-fit smoothing alone is insufficient.

Experiments 0109–0110 locate the long exterior sheets in coarse-mask support and test an actual image-depth-driven head candidate. An inset skin patch excludes the sheets but is not a full head; camera metrics remain failed. The bounded candidate slightly improves the right profile while worsening the left and retains generic/open-mouth appearance. It is `REJECT`, not a visual improvement. All 88 public tests pass.

Experiment 0108 isolates ray representation without another model run: exact pinhole unprojection of unchanged depth makes own-view alignment exact, but dense transfer p95 remains 91.93 px and actual cross-view sheets persist. Candidate `REJECT`; native-ray approximation is not the sole cause. No camera, template or texture promotion.

Experiment 0107 tests one explicit uncalibrated 1800 px focal condition. The model does not enforce supplied intrinsics; camera p95 worsens to 51.48 px and visual promotion is `REJECT`. A new diagnostic finds 18–26 px own-view errors between native dense rays and their fitted pinhole cameras, despite correct rigid pose conversion. The optional conditioning path is tested; 88 tests pass, with no accepted visual improvement.

Experiment 0106 completes actual offline Apache MapAnything inference on all five photographs in about 79 seconds on CPU. Its raw camera check is `REJECT` at 48.58 px held-out p95, focal plausibility fails, and observed-surface renders are not coherent across views. The asset-locked adapter and pose conversion run successfully; this is not an accepted head or visual improvement. The full public suite passes 87 tests.

Experiment 0105 executes standard and affine/domain-size-pooled SIFT with the same five photos and masks. Standard matching has no verified pair; the affine candidate has only one 26-inlier frontal/oblique pair, no profile connections and no recovered sparse model. Both reconstruction attempts are `REJECT`. The new runner preserves input rights and checks actual mask use; it does not establish accepted cameras.

The camera and full visual acceptance gates have not passed. Experiment 0104 verifies 44 additional CC0 nose/lip assets and tests a 32-control basis reduced to eight local directions. Aggregate profile and point fitting errors decrease under bounded step selection, with valid triangle and visibility checks, but actual five-view and enlarged mouth renders retain generic identity and an open/angular mouth. The numerical report remains `UNVERIFIED`; the candidate is `REJECT` for visual promotion. These fitting/selection metrics are not held-out validation. KeenTools-level parity remains `UNVERIFIED`.

## How to verify the public code

From `C:\workspace\headfoundry`:

```powershell
C:\Python313\python.exe -m pip install -e .
C:\Python313\python.exe -m unittest discover -s tests -v
C:\Python313\python.exe -m headfoundry.camera
C:\Python313\python.exe -m headfoundry.vggt tests\fixtures\vggt_camera_point_fixture.json
```

The repository is a library and experiment workspace, not a long-running service, so there is no start/stop procedure or deployment target. Publishing currently means committing reviewed public changes and pushing `main`; it does not publish private assets or constitute model-quality acceptance.

## Next gate

The next gate triangulates only left/right-consistent masked disparities from
the two classical stereo pairs, fuses them in the fixed world frame and tests
the resulting front-face surface in the unused pure-profile views. Reject
disagreement, negative depth or failed mesh safety. Even a technically valid
surface must beat experiment 0132 on bilateral held profiles and show a visible
exact-Blender-overlay gain before promotion.

Resolve the neutral mouth's surface/closure configuration with complete rim support on the evaluated surface and actual frontal/oblique/profile evidence before further identity fitting. Re-lift attachments after topology changes; never reuse old triangle IDs silently. Do not repeat two-point attraction, amplify mouthClose, or amplify the rejected depth-ray direction. Inset observed patches are not full heads and cannot establish camera accuracy. All camera, anatomy and visual acceptance gates remain unchanged.

## Known pitfalls

- A model or repository license does not automatically grant rights to every checkpoint or training dataset.
- Positive depth, valid matrices and lower reprojection error do not prove correct camera calibration or identity reconstruction.
- Shrinking internal lip gaps, valid triangle orientation and sampled no-crossing sections do not prove natural closure or full collision freedom.
- Actual photos and derived biometric/identity artifacts are local-only under the current consent and must not enter Git, PCR or public reports.
