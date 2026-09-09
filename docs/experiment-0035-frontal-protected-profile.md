# Experiment 0035: profile depth fitting with frontal projection protection

Status: `UNVERIFIED` experimental geometry, not an accepted likeness. Camera
failures from previous experiments are unchanged. No production baseline replaced.

## Target and controlled experiment

Fit the nose/lip/chin outline without moving frontal image positions. Use the
unchanged camera matrices, anatomical template and original five photos from
0034. The primary variable is local geometry displacement. Existing approximate
profile curves (0032, 5–10 px reading uncertainty) are fitting inputs, not truth.
Do not change annotations to match the result. No texture or generated images.

The first unconstrained trial moved frontal nose/chin anchors by 4.66/7.95 px.
It is retained privately as `template-profile-v1`, not adopted. The second trial
uses one displacement degree of freedom per vertex along its fixed frontal
camera ray. This makes frontal projected vertex positions mathematically
invariant while permitting depth changes. Existing sparse surface fitting,
six-ring locality, protected outside vertices and normal/area backtracking are
reused; default unconstrained behavior remains unchanged.

## Executed evidence

Candidate: `assets/private/subject-001/template-profile-v2/candidate.obj`.
Fit report and three-view original/baseline/candidate image are beside it.
All-five-view audit: `template-profile-audit-v1/five-views.png` and `report.json`.
Both images were inspected. The source `registered.npz` SHA-256 is
`83d9f1ee7499f8a3b1c8ea4e91337e2307b2a2adf0f10918e5a07b7c32927ef4`.
The frozen contour SHA-256 is
`84ab7545b80b277d62bc7b45d82eb9585e8d9cb24dcfe7d5f0e3d0b281218673`.
Input consent and original-photo digests are checked; nothing identifiable is
committed or uploaded. Local runners: `fit_template_profiles.py` and
`audit_template_profiles.py` under the private subject directory.

- 17/16 selected profile constraints; maximum displacement 0.03 template units
  after backtracking (not millimetres; no physical scale calibration).
- All-vertex frontal maximum projection change: 3.22e-13 px.
- No reversed triangle normals; minimum area ratio 0.634 relative to baseline.
  These checks do not establish absence of self-intersections.
- Exact projected edge/row envelope mean absolute horizontal error against the
  fitting curves: left90 8.236 → 6.184 px; right90 11.449 → 9.899 px.
  Some individual samples worsen; residuals remain material relative to reading
  uncertainty. They are not held-out scores or evidence of overall likeness.

The mesh remains coherent but coarse and largely generic. Small profile changes
are visible; cheek/jaw, eye and neck deficiencies remain. Frontal pixel invariance
does not preserve normals, shading, occlusion order or perceptual identity. No
verified likeness improvement or KeenTools parity is claimed.

## Checks and next gate

58 tests pass, including synthetic ray-constrained depth recovery, finite/nonzero
direction checks, bounded profile-step projection invariance and invalid frontal
projection rejection. Existing unconstrained surface tests still pass.

Next: replace sparse nearest-vertex envelope associations with continuous
surface constraints and inspect pose/outline ambiguity before larger deformation.
Keep actual multi-view clay evidence and frontal protection; do not remove safety
backtracking just to reach a curve. Full-head identity, ears/eyes/neck, texture,
export and independent camera/visual acceptance remain incomplete.
