# Experiment 0039: original-photo oblique boundary evidence

Status: boundary observations `UNVERIFIED`; geometry trial not adopted. No
visual acceptance or new baseline. This follows 0038's observation-semantic
failure, not a change to its frozen detector observations.

Ten separate boundary observations were localized directly from the original
two oblique photographs. AI-read seed windows span +/-18 horizontal pixels;
the local RGB contrast across each candidate edge is averaged over five rows.
No mesh, camera, detector oval or fitted output participates in choosing the
edge. All ten peaks lie inside their search windows. Windows, complete contrast
scores, photo hashes and resulting points are recorded privately.

The original-photo overlays were inspected **before** using these readings in
any fit. They follow the visible cheek/chin/background boundary substantially
better than the interior detector oval. This is still an approximate seeded
measurement: a color edge is not guaranteed anatomical truth, sample size is
small, and no human annotation or scan validation is claimed.

Private evidence: `oblique-photo-boundaries-v1/observations.json` and
`original-overlays.png` under the consented subject directory; local runner
`read_oblique_boundaries.py`. Input rights/digests are validated before image
processing. Nothing identifiable is published or transferred externally.

## Fixed-condition geometry check

The same source mesh, camera matrices, front-half ROI, protected region and
frontal-ray constraint used in 0038 were retained. Only the oblique observations
changed. The original observations and rejected candidate remain untouched.
The local run produced `oblique-jaw-v2/{candidate.obj,report.json,five-views.png}`;
the five-view original/baseline/candidate clay sheet was inspected.

- left30 new-boundary fitting MAE: 5.849 → 5.780 px.
- right30: 5.944 → 5.524 px.
- Maximum vertex displacement: 0.008062 template units.
- All protected vertices remain exact; maximum frontal projection change
  3.60e-13 px. Existing central profile residual arrays remain unchanged.

These numbers use different observations from 0038 and must not be presented
as a geometric improvement from its 19.8/12.4-pixel errors. The informative
result is that the independently located boundary contradicts that earlier
error interpretation. The actual new shape change is negligible; it is not
adopted. Two upper samples per view still have approximately 11-pixel errors
and remain unchanged by the protected-region fit.

## Next action

Do not repeat a frozen-region optimizer against constraints it cannot change.
Audit the exact support vertices and anatomical extent of the protected core,
then design a bounded cheek region that protects true eye/nose/mouth geometry
instead of freezing an oversized image rectangle. Camera uncertainty remains
a competing explanation; do not equate local fitting ability with correctness.
The full likeness, anatomy, texture and independent acceptance objective is
still incomplete.
