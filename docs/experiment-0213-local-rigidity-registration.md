# Experiment0213: locally rigid cross-source surface registration

Pre-registered2026-10-17 before implementation/run. No photograph fitting.
0210 reduced distances but produced posterior/neck kinks; its patch field is
frozen. 0211 rejected forcing hidden lip supports together, and0212 rejected
transferring edited-source coefficients directly to native topology. Do not
reopen any of those fits or change production assets.

## One different hypothesis

Use local rotation-aware edge preservation instead of unconstrained patch
translations. Independent NumPy/SciPy implementation of the local/global idea
in [Sorkine and Alexa,2007](https://igl.ethz.ch/projects/ARAP/): estimate proper
per-vertex rotations by SVD, then solve a sparse positional system. No CGAL or
third-party implementation/model is adopted. Positive-clipped cotangent edges
make our variant's squared energy nonnegative; disclose clipping and meshing
dependence. This is not a volume, collision or anatomical guarantee.

Change only this deformation representation/objective. Reuse0210's existing
licensed FLAME2023 Open targets, exact GNM30 baselines, source topology/placement,
sampling seeds, compatible-normal matching,90% trimming, neck scope, fixed
cameras, held surface samples and30% numeric gate. Existing edited GNM skin is
only a benchmark control, not a new endorsement of hidden contact semantics.
Do not substitute native topology or generate easier/smaller target identities.

Start from each frozen GNM30 prior. Rest-edge weights are summed half-cotangents,
clipped to1e-8 and normalized by their median. Data weights are0210 matching
weights normalized to mean1, times0.05. Fixed10 closest-surface outer updates,
20 local/global iterations per update. All choices fixed before the first case;
no strength, edge-weight, iteration, scope or source-coefficient sweep.

After each outer trial, use the existing at-most12 deterministic safe half-steps
against the original aligned mean: minimum area>=0.5, zero normal reversals,
maximum displacement<=0.12 radius. A failed safe update ends that case. Record
trial energies and safe steps; no post-fit shrink, smoothing or topology edits.
Save/re-read17-decimal OBJ before final implemented safety/metric checks.

## Staged stop and advancement

Run case00 first, with the same independent evaluation as0210. To continue it
must pass implemented mesh guards, reduce symmetric sampled RMS>=30% over the
frozen first30 baseline, and avoid >5% nose/lip/chin or any fixed-view depth
regression (same1e-8 tolerance). Then render target/prior/new candidate in all
five views and inspect whole heads and nose-lip-chin crops. A kink, fold or lack
of meaningful visible target-shape recovery stops before the other cases.

Only if that screen passes, process the remaining three original cases. The
full gate remains all four safe/protected and at least3/4 reaching30%, followed
by actual five-view review. Passing would establish limited synthetic
registration evidence, not true anatomical correspondences, an accepted
reference-photo head, physical cameras, trained predictor or KeenTools parity.

Budget:<=15 minutes fitting/evaluation,<=15 minutes render/review, one main run.
One correction rerun only for a diagnosed implementation error, never a quality
miss. If rejected, freeze this exact scheme and do not apply it to the five
independently generated AI references. No model download, training, hair,
texture, photo upload or default/head/camera change.

## Results

Completed the single case00 screen in76.371s. All10 outer trials accept full
safe steps (zero halvings); no coefficient changes, corrective fitting rerun or
parameter sweep. The local/global energies decrease in each fixed-observation
solve; minimum final proper-rotation determinant0.9999999999999973. Of33894
rest edges,5762 require the predeclared positive clipping, including near-zero
diagonal weights. Do not describe this as an unmodified cotangent implementation.

| Case00 measure | Frozen GNM30 | Locally rigid candidate |
|---|---:|---:|
| Symmetric sampled RMS / radius | 0.04196115 | 0.03647164 |
| Nose-region RMS / radius | 0.01462347 | 0.00948885 |
| Combined-lip RMS / radius | 0.00968329 | 0.00797210 |
| Chin-region RMS / radius | 0.02148861 | 0.00691619 |
| Left-profile depth RMS / radius | 0.06427430 | 0.05215897 |
| Right-profile depth RMS / radius | 0.06178459 | 0.05036685 |

The actual exported candidate passes implemented guards: minimum area0.568024,
zero reversals, maximum displacement0.0774981 radius. All protected regional
and five-view depth checks pass. But the overall gain is only**13.08%**, below
the predeclared30% requirement: **numeric gate `REJECT`**. This is similar to
0210's13.56% on the same case, not a decisive new registration result.

**Stop executed:** do not process cases01–03 or render this candidate, do not
adjust strength, clipping, iterations, source coefficients, scope or safety.
The no-kink visual hypothesis is therefore `UNVERIFIED`, not passed; triangle
safety cannot establish that appearance. No new person head, white-mesh quality
comparison, photo fitting, physical camera claim or default change occurred.

## Read-only residual attribution, not another fit

The separate `tools/audit_registration_residuals_0213.py` replays the final
matching rule and attributes area-weighted **source-vertex forward squared
proximity**. This is a diagnostic quadrature, not the independent sampled
symmetric score and not a replacement acceptance metric:

| Final source scope partition | Area share | Forward squared-error share |
|---|---:|---:|
| Supported | 82.304% | 6.185% |
| Normal-incompatible | 1.522% | 0.157% |
| Distance-trimmed | 16.174% | 93.658% |

The inherited rule trims10% of compatible **vertices**, not10% of area. It gives
unsupported points a target at the frozen prior with fourfold rest weight.
Most residual error is therefore outside actual target observations, and held
toward the old head. This is evidence of an observation/coverage concern, not
proof that removing trimming will be correct. Source facial-region labels cover
23.73% of scoped area but only0.536% of this residual error; the remaining skin
has not yet been anatomically localized. Do not call all of it "posterior head"
or assume it is valid corresponding anatomy rather than neck/aperture/domain
mismatch. Overlapping individual region labels cannot be summed.

Next discriminating gate: **localize and validate the ignored target/source
geometry before changing a matcher or doing another subject fit**. Preserve the
same four target heads and full evaluation denominator. Neither a mask shrink,
discarding difficult regions from evaluation nor a larger deformation field is
justified by this audit. Any genuinely different observation strategy needs its
own hypothesis and bounded experiment;0213 remains frozen and rejected.

## Reproduction/evidence

Three focused solver checks cover rigid rotation/translation, proper rotations,
non-rigid energy descent and invalid/unanchored inputs. All127 public tests pass.
No new dependency, model, dataset or rights scope was introduced. Primary source
supports the local/global principle, not these quality claims or freedom to use
unreviewed third-party code.

```text
.venv/Scripts/python.exe tools/experiment_0213.py
.venv/Scripts/python.exe tools/audit_registration_residuals_0213.py
.venv/Scripts/python.exe -m unittest discover -s tests
```

The first command refuses overwrites; it is only for fresh-output reproduction
with the locked0210 capsule available. Local meshes, fixed cameras, saved arrays,
per-update energies/guards and exact provenance are in
`artifacts/experiment-0213/`. `residual-audit.json` additionally records exact audit
inputs and code hashes; no mesh/photo derivative is uploaded to Git or PCR.
