# Experiment 0014: independent anatomical reading check

Status: UNVERIFIED. The existing camera candidate remains REJECT. No new
geometry, texture or camera baseline is promoted.

Original-pixel grids were rendered for the eyes, nose and mouth in the three
front/intermediate photographs. Four canthi and two mouth corners were read
visually by the assistant before computing predictions. Coordinates were
frozen in a private JSON record with subjective reading radii of 4 px, or
6 px for the two less-clear far outer canthi. These are AI-assisted manual
estimates, not independently human-verified or calibrated ground truth.
Detector coordinates were used to locate generous crops only; no detector or
camera markers were displayed during reading. Nostril/alar landmarks were
excluded because the far side is not clearly visible in all views; pupils and
specular highlights were not used as rigid face landmarks.

The cameras from experiment 0012 stayed fixed. For each of the six points,
triangulate from two manual observations and predict the third, cycling all
three target views. None of these new readings was used to fit a camera.
This gives 18 comparison residuals, not 18 independent subjects or trials.

- Median reading-to-prediction distance: 3.049114 px.
- p95 reading-to-prediction distance: 8.226014 px.
- Largest residual: 8.362766 px at a side-view outer canthus.

A 500-draw deterministic perturbation check samples each image coordinate
uniformly within its declared reading radius (seed 1401). Its 5th/95th
percentiles are sensitivity bands, NOT statistical confidence intervals;
camera uncertainty and expression changes are not included. This check shows
that reading uncertainty is materially comparable to the 3 px camera target.
It cannot validate the camera gate or establish a precise correction.

The original-photo overlay was rendered and inspected. Eye and mouth anchors
are broadly close under the fixed cameras, with remaining corner offsets.
This is useful counter-evidence against treating the cameras as wholly wrong,
but says nothing sufficient about forehead, cheek, jaw, profile or full-head
accuracy. The landmark population differs from the dense detector audit, so
the smaller error is not an improvement claim.

The photo hashes and local processing consent were checked against the run
manifest. Annotation JSON is hashed in the private result to preserve which
frozen readings were tested. All images and identity-specific outputs remain
local and ignored by Git. No external model or service was used.

Next gate remains precise, independently checked camera/shape evidence. The
available manual reading must not be silently promoted to subpixel truth or
used to lower the 3 px threshold. Before optimizing against these points,
retain this independent check and reserve a separate validation set.
