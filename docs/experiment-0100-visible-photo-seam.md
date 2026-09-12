# Experiment 0100: visible photo seam candidates

Status: `UNVERIFIED` image observations, no geometry update.

Trace forty-one columns between the existing detected mouth corners in each
front/oblique photo. Use a piecewise-linear corner/center prior with a +/-8px
vertical search window. Normalize local luminance per column, then minimize a
dark-line cost with offset and adjacent-offset smoothness penalties by dynamic
programming. This reuses the local photos and existing NumPy/Pillow; no new
weights or external image service.

Actual original/overlay crops were inspected. The curves broadly follow the
closed visible lip seam in all three views. No trace hits the search boundary;
maximum offset from the initial prior is 4.5335/3.1460/3.3980 px. This is not
measured localization accuracy. Lighting, shadows, integer row sampling and
the detector prior can bias the traces; endpoints are not anatomical truth.

Private `photo-seam-v1` stores all pixel coordinates, initial priors, source
photo hashes and the inspected overlay. Input consent is verified before
reading images. These are local-only derived personal data and are not committed.

Next match a model's visible seam to these image curves with per-view support
and occlusion checks. Do not pair equally indexed points across views as exact
3D correspondences, or use hidden contact candidates as visible curve points.
No identity, camera or geometric acceptance is claimed. Public production code
is unchanged; verification here is actual extraction and source-image inspection.
