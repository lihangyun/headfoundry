# Experiment 0013: correspondence identity and conditioning audit

Status: UNVERIFIED diagnostic; the existing camera candidate remains REJECT.
No detector point has been silently removed or replaced to improve a score.

Under the fixed experiment 0012 cameras, each of the 60 held-out observations
was predicted from its other two training observations using linear
triangulation. Finite differences of 0.1 px in each of the four training
coordinates estimate the largest singular value of the held-out projection
Jacobian. This is fixed-camera local sensitivity, NOT a full uncertainty
estimate: it omits camera uncertainty and systematic correspondence bias.

- Median worst-axis noise gain: 1.856191.
- Maximum gain: 2.294254.
- Minimum angle between the two training rays: 30.891088 degrees.

The six largest-error correspondence triplets were rendered from original
photos and visually inspected. They are indices 104, 435, 143, 156, 52 and 169.
Several lie on weakly textured forehead/cheek regions or near view-dependent
silhouettes; the crops do not provide identifiable physical marks proving that
equal detector indices locate exactly the same material point across views.
This is not a corrected annotation set and does not prove detector failure at
each point. The observed angles do not support near-parallel triangulation as
the sole explanation for these discrepancies under the assumed cameras.

An independent photometric check extracts SIFT inside eroded face masks. The
detector is used only for the mask; no fitted camera or epipolar condition is
used to choose matches. With a fixed 0.75 descriptor ratio and mutual matching:

- Features: 1272 / 1035 / 1130 for front / left30 / right30.
- Mutual pairs: 5 / 9 / 5 for front-left / front-right / left-right.
- Three-view cycle-consistent tracks: 0.

This is failure of this specific matching configuration, not proof the photos
are unusable, synthetic, or impossible to reconstruct. No automatic texture
track set is promoted as independent geometry evidence. There are too few
supported tracks here to replace the camera observations.

Next action: explicitly identify a small set of visible anatomical landmarks
in original image coordinates, document annotation uncertainty, and compare
against a held-out manual set. Smooth-skin mesh vertices and silhouettes must
not be treated as exact physical tracks. Keep manual evidence distinct from
detector predictions and from camera-projected guesses.

All original photos, masks, crop comparisons, scripts and numerical records
remain local in ignored storage. No photos were uploaded; no new dependency
or weight was installed. The existing 34-test suite still passes.
