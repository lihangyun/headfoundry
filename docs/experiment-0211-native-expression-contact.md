# Experiment0211: native lower-face expression contact

Pre-registered2026-10-17 before expression fitting. No photographs or camera fit.
Hypothesis: an anatomical lower-face expression subspace may close the lips
without the roll/skin artifacts of manually adapted closure or free XYZ fields.
Counter-risk: PCA directions need not encode a neutral closed mouth within bounds,
and small pairing errors can force an unnatural expression. Numerical rank is not
anatomy evidence.

## Fixed asset, controls and objective

Use the same exact Apache-2.0 GNM v3.0 checkpoint SHA256
`785d62572590b1073d3f93c61d82346c1e33ffacd3f8245a1b6e0b33cf59e13d`.
Only its150 `lower_face_region_*` expression fields; no semantic-sampler `.h5`
models, new download, neural training, paid asset or additional person data.
The source has neck/head/eye joints, **not a jaw joint or a semantic mouthClose
control**. This experiment does not invent such labels.

Primary comparison: original skin (12466 vertices/24820 triangles) with expression
zero versus expression-closed skin with **identical topology and identity**.
Generic source eyeballs are added unchanged in both rendered conditions. The
current manually closed donor is a visual context column only: it has different
exterior/weld topology and is not an isolated basis comparison or3D ground truth.
No mesh welding, triangle removal, free-vertex fit or post-fit smoothing.

Three development cases: mean and two deterministic first30 identity vectors,
seed20261017, Gaussian sigma0.5 clipped to+/-1.5. If an identity source violates
zero-reversal/area>=0.5/displacement<=0.12-radius checks, halve its complete vector
at most ten times before expression fitting; record the scale. Identity, eyes,
pose, lighting and camera then stay fixed.

One bounded quadratic solve per case, expression coefficients+/-3. Objective:

-29 previously identified original lip-support pairs,87 XYZ gap residuals with
  fixed native-unit sigma20e-6;
- area-weighted whole-skin expression displacement, sigma1e-3 native units;
- coefficient prior sigma3.

Use the original source expression fields directly, not the previous manually
closed identity derivative. No parameter sweep. This is a contact/neutral-source
screen, not identity reconstruction or a claim that correspondence pairs are
perfect anatomical contact locations.

## Gates and stop

Require all three actual17-decimal exports to satisfy:

- maximum pair gap<=20e-6, median<=10e-6 native units;
- contact-midpoint drift<=0.75e-3 native units;
- positive upper/lower outward lip relief on central source columns |x|<0.006,
  each at least50% of its source value;
- zero proper upper/lower strip crossings away from a20e-6 contact neighborhood
  in21 fixed x sections spanning+/-0.015 (offset1.414e-8 avoids exact vertex cuts);
- source-relative minimum triangle area>=0.5, no normal reversals, maximum skin
  displacement<=0.02 fixed source-mean radius; finite coefficients within+/-3.

These section tests do not certify collinear overlap, whole-head self-intersection,
inside-mouth/teeth collision or solid lip volume. Actual five-view and enlarged
mouth renders must additionally show natural relief/contact and no pucker, ledge,
crease or protected-view defect. No default promotion in this experiment.

Budget: one10-minute fit/audit run and one10-minute render/review run, at most one
correction for a diagnosed implementation error. Failed anatomy, bounds or quality
is **not** an implementation bug. No retuned sigma, identity amplitude, coefficient
bound or alternate source-row choice. Unsafe candidates are rejected before
rendering; safe failed candidates may be inspected without being promoted.

Only after all source/contact and visual checks pass may this closure mechanism
be tested on a separately recorded, unchanged subject identity. Until then the
five independent AI references, subject mesh/cameras and defaults remain untouched.

## Results

Completed one frozen run in6.961s, no correction fit or sweep. All three source
identities required no safety halving. All123 public tests pass. None of the
optimized candidates is rendered or applied to the subject.

| Case | Max gap, native units | Midpoint motion | Min relief ratio | Min area ratio | Reversed triangles |
|---|---:|---:|---:|---:|---:|
| 00 | 0.00002936 | 0.00370686 | 0.18457 | 0.07148 | 8 |
| 01 | 0.00002789 | 0.00390228 | 0.20890 | 0.07946 | 9 |
| 02 | 0.00002912 | 0.00512322 | 0.11542 | 0.05226 | 8 |

All three hit the coefficient bound3, fail contact/midpoint, relief and full-skin
safety gates. Maximum displacement0.02504–0.03123 radius exceeds0.02. The21
upper/lower-strip section checks happen to find no proper crossing outside the
contact neighborhood; **that does not rescue the flipped/flattened whole skin**.
The failed raw candidate meshes and coefficients are retained, not shrunk,
smoothed, welded or replaced with a safer-looking output.

Independent replay from the saved expression field/coefficients reproduces the
actual17-decimal skin export to5.56e-17 native units. Bound-aware first-order
optimality residuals are1.06e-8–1.25e-8 versus right-hand-side norms1.59e5–2.67e5.
The pinned upstream bind-pose implementation explicitly adds identity and
expression displacement fields, matching this implementation. These controls
support a failed constrained experiment, not a solver/API integration bug.

**Decision:** contact construction `REJECT`; execution checks
`TECHNICAL_CHECK_PASSED`; actual photo likeness `UNVERIFIED`. Do not retune the
same weights/bounds or substitute another source row. No default/camera/head
change, photograph inference, semantic sampler or neural training.

## Post-failure semantic audit: the assumed contact row is hidden

`tools/audit_native_contact_visibility.py` performs a separate read-only first-hit
audit of the **unchanged native mean**, not another expression solve. It checks
the exact pinned model and saved supports before projecting58 original-row1
points (29 upper+29 lower) through each fixed camera; visibility tolerance5e-6
native units. Results:

| View | Assumed row1 visible | Row2 visible | Row3/row4 visible |
|---|---:|---:|---:|
| Front | 0/58 | 56/58 | 58/58 each |
| Left/right30 | 0/58 each | 56/58 each | 58/58 each |
| Left/right90 | 0/58 each | 24/58 each | 28/58 each |

Row1's median first-hit offset is0.00047667 front,0.00060419/0.00061105 obliques,
and0.00866682/0.00880423 pure profiles. This row lies behind other native lip
surfaces and **cannot be labeled the observed visible lip seam**. Hidden points
could participate in physical contact, but that would require independent
anatomical evidence, not the photographic appearance assumed in earlier closure
work. No alternative row has been fitted or adopted as a replacement contact.

This also exposes an unverified premise in the pre-registration/raw run labels:
calling expression-zero skin "open" was an assumption, not a measured external
mouth opening. The original record is preserved; new reference panels use
**unchanged native source**, not "open" or ground truth.

### Source-only rendering, excluding every unsafe fitted result

Two separate hash-checked reference capsules contain only the unchanged native
mean and existing manual-closure context, with the same unchanged source eyes.
The shared renderer's explicit source-reference mode cannot include a `candidate`
variant and checks each reference OBJ hash. No unsafe optimized expression OBJ is
copied or rendered. Standard five views plus a common4x focal inspection zoom
produce20 source/context images. Macro extrinsics, geometry and lighting are
unchanged; both columns share the same centered inspection camera. This is not
camera reconstruction or an edit of subject cameras.

The inspected macro five-view sheet shows a **closed-looking visible seam already
on the untouched native mean**. It is not an obviously open mouth that justifies
forcing a hidden material row to zero. The manual context differs in interior/
exterior and weld topology (e.g. nostril appearance), so this is not proof that
every visible difference is caused only by the lip displacement. It does not
certify collision freedom, a true contact surface or identity likeness.

**New next action:** stop speculative forced closure and test the original native
**exterior** as a controlled source-construction ablation with frozen identity and
cameras. First reproduce the existing manual baseline exactly, then compare the
native exterior without changing coefficients, fitting observations or texture.
This is a new diagnostic, not applying the failed expression solution to a person.
Until that A/B exists, no claim that removing closure fixes the subject is made.

## Evidence and reproduction

- `artifacts/experiment-0211/`: raw failed candidates, source skin, coefficients,
  supports/field, report and `source-visibility.json`; no unsafe renders.
- `artifacts/experiment-0211-source-only-review/`: ten unchanged source/context
  five-view reference renders and comparisons.
- `artifacts/experiment-0211-source-mouth-macro/`: ten common4x inspection renders,
  comparisons and explicit non-reconstruction camera metadata.
- Exact model/source hashes, render projection checks and code identities are
  retained locally. No private materials or asset bytes in Git/PCR.

```text
.venv/Scripts/python.exe tools/experiment_0211.py
.venv/Scripts/python.exe tools/audit_native_contact_visibility.py
blender --background --python tools/render_capacity_0208.py -- artifacts/experiment-0211-source-only-review
blender --background --python tools/render_capacity_0208.py -- artifacts/experiment-0211-source-mouth-macro
.venv/Scripts/python.exe tools/review_capacity_0208.py artifacts/experiment-0211-source-only-review
.venv/Scripts/python.exe tools/review_capacity_0208.py artifacts/experiment-0211-source-mouth-macro
.venv/Scripts/python.exe -m unittest discover -s tests
```

All run/capsule outputs refuse overwrite. Native original versus expression
comparison is numerically audited on identical full-skin topology; the differently
topologized manual donor remains context only, never geometric ground truth.
