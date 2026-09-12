# HeadFoundry product requirements

## Product goal

HeadFoundry reconstructs an editable, neutral full-head 3D asset from ordinary multi-view photographs. The target is believable identity, frontal features, bilateral profiles, ears, skull and neck transition from held-out views. OBJ and GLB are the first delivery formats; stable topology, texture and expression support follow only after geometry acceptance.

## Inputs and rights

- Accept 5–10 sharp, neutral photographs with useful frontal, oblique and bilateral profile coverage.
- Bind every input and model asset to a versioned manifest containing its SHA-256, source, license, allowed purpose, retention policy and consent.
- Fail closed when provenance, commercial-use rights, biometric consent or file integrity is missing.
- Keep private photographs, biometric annotations, identity meshes and derived visual evidence out of Git and external context services unless separately authorized.

## Reconstruction requirements

1. Validate image count, resolution, clarity, duplicates and view coverage with actionable errors.
2. Recover physically consistent cameras with explicit matrix and coordinate conventions, plausible focal lengths, positive-depth checks and held-out reprojection evidence.
3. Fit a coherent full-head prior using shared neutral identity and per-view pose/expression, preserving topology and recording observed versus inferred regions.
4. Add detail and texture only after coarse geometry passes; choose source pixels by visibility, angle and sharpness, with explicit handling of unobserved areas.
5. Export reproducible assets and retain the exact input, model, code and parameter identities used for each accepted result.

## Acceptance contract

- `TECHNICAL_CHECK_PASSED`: a bounded engineering check passed; it is not visual acceptance.
- `UNVERIFIED`: required evidence has not been collected.
- `REJECT`: a required gate failed or is missing.
- `PARTIAL_SUCCESS`: numeric gates pass without complete licensed visual evidence.
- `ACCEPT`: all protected camera, geometry, topology, texture and held-out visual gates pass with licensed evidence.

No result may be described as KeenTools-level quality without complete visual evidence. Reduced fitting residuals alone cannot establish likeness, correct anatomy, natural surface contact or collision freedom.

## Product boundaries

- Independent clean-room implementation only; do not use Peek implementation code or KeenTools private sessions, outputs or services.
- Free-commercial models and infrastructure may be adopted after exact license/checkpoint review and hash locking.
- Paid or inaccessible components require an independent alternative; never silently substitute research-only or non-commercial weights.
- Experimental geometry is allowed before camera acceptance, but remains unaccepted and must not be concealed by texture or generated imagery.

## Current milestone

The current milestone is a truthful end-to-end validation slice: rights-aware inputs, camera initialization and gates, experimental full-head geometry, fixed-support diagnostics and real five-view comparisons. The immediate visual focus is improving side-profile and mouth reconstruction without regressing protected views.

