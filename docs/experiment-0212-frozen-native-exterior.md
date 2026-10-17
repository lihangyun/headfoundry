# Experiment0212: frozen-identity native exterior ablation

Pre-registered2026-10-17. Motivation:0211's assumed row1 is hidden0/58 in all five
native-mean views, and untouched source renders already show a closed-looking seam.
This does not prove the subject is fixed; test the construction premise directly.

One primary variable: native GNM exterior versus the manually adapted closure
construction. Use the existing0206 experimental identity (30 coefficients), its
seven fixed pose/scale parameters, the original source-to-world similarity,
generic eyes and cameras **unchanged**. The0206 head is a rejected experimental
baseline, not the production/default head. No new optimization, expression fit,
contact-row substitution, free deformation, texture, hair or model download.

Native exterior uses the exact checkpoint's `skin_exterior` group (11460 vertices,
22636 triangles), preserving original mouth topology instead of removing posterior
rows and welding row1. Both paths use the same two finite Catmull-Clark steps.
Topology differences near the lips are inherent in the source-construction
variable; do not attribute an outcome to a displacement-only scalar ablation.
Unlike0211's full-skin reference, this exterior control does not add inner-mouth/
nostril geometry as an unrelated visual advantage. Identical source eyes remain.

## Replay, rights and protected checks

Validate the five-image local-validation consent/rights manifest and all exact
source, basis, identity, camera and scene hashes. The five AI references are
independently generated/composited: comparison is design-reference matching, not
proof of one physical subject/camera. No image or derivative uploads.

First regenerate the original0206 baseline through its real source/refinement/
pose path: full exported vertices must agree with its saved fit to<=1e-12 and
topology exactly. Reuse its original OBJ/white renders only after source, camera,
photo, scene, renderer and per-image hashes verify. Never overwrite that baseline.

For the candidate, inherit the original<=0.06 world-unit shape displacement,
minimum area ratio>=0.5 and no source-relative triangle reversals on cage and
actual refined surface. This is not whole-head collision/volume certification.
No post-fit scaling or safer-coefficient substitution. Eyes must replay identically.

Compare up to1000 deterministic common material-chart points outside the original
closure support plus five source adjacency rings. This protects unaffected
forehead/nose/outer-face/neck regions against new placement or smoothing drift;
maximum replay difference<=1e-10. It does not establish anatomical correctness.

Render only if technical guards pass, using the existing saved subject clay scene,
original1254px intrinsics/extrinsics and exact five-view lights/material/exposure.
Compare original AI reference /0206 baseline /native exterior at common crops.
Any mouth opening, ledge, pucker, fold or protected-view regression rejects the
candidate. No clear multi-view visual gain means no promotion either. No `ACCEPT`
or KeenTools parity claim follows from replay, a tiny gap or a numerical change.

Budget: one10-minute prepare/replay run and one10-minute render/review, at most one
correction for a diagnosed implementation error. No refit, coefficient/safety
relaxation, extra subdivision or row/weight sweep. Failure stops this frozen
ablation. Production head/cameras/defaults remain unchanged in every outcome.

## Results

Completed one45.443s preparation/replay run. No refit or correction rerun.

- Original0206 full exported surface and topology replay exactly (maximum
  coordinate difference0). All1000 protected common charts agree to7.03e-16
  world units; eyes agree to6.94e-18.
- Cage: minimum area ratio0.638638, zero normal reversals, maximum identity
  displacement0.059997 world units: implemented checks pass.
- Actual two-step refined surface: minimum area ratio0.199493<0.5, zero normal
  reversals, maximum displacement0.059980: **REJECT** before rendering.
- A read-only witness audit finds8 subthreshold refined faces. The worst belongs
  to original source face10722, in the original lip rows and absent from the old
  manually constructed surface. Seven of the eight have parents absent from that
  old surface. This explains why old-source fitting did not constrain all new
  faces; it does not authorize excluding them or lowering the area threshold.

Thus fixed coefficients optimized on the edited construction cannot simply be
transferred to the native one under the same guards. This does **not** establish
that a properly fitted native model is incapable of the target shape, nor that
the native visible seam itself needs forced closure. No white-mesh rendering of
this candidate, photo-quality comparison, coefficient shrink or default change
occurred. Real-reference likeness is `UNVERIFIED`; promotion is `REJECT`.

Freeze this ablation, not the whole model. Do not silently turn it into another
identity fit or alternate source-row closure search. In particular the hidden
contact-row finding from0211 is a correspondence warning, not a new visible
photo landmark. ADR0002's distinct geometry/observation evidence requirement
remains in force before another expensive subject fit.

Public driver: `tools/experiment_0212.py`. One focused regression test ensures
that small displacement cannot hide excessive area compression or a reversal;
all124 public tests pass. Reproduce only into a fresh output (the runner refuses
overwrite): `.venv/Scripts/python.exe tools/experiment_0212.py`.
The exact source/camera/photo/scene/export locks, replay arrays and rejected
meshes remain locally in
`assets/private/subject-001/native-exterior-frozen-0212/`.
