# Experiment 0005: weight-independent perspective landmark bundle

2026-09-05. Real-photo camera gate: REJECT. Full-head quality: UNVERIFIED.

Implemented joint perspective fitting of sparse 3D landmarks and camera poses.
The initial frontal pose, supplied intrinsics, and regularized shape prior fix
gauge and scale. The supplied focal length is an assumption, not calibration.
Outputs include genuine 3x4 extrinsics, 3x3 intrinsics, and projected landmarks.
No external checkpoint, head asset, or training data was used.

The primary experimental variable is landmark-based camera initialization.
The first trial uses the frontal and two intermediate user-consented photographs,
12 approximate manually observed anatomical landmarks per photograph, and six
held-out observations. The profile photographs are excluded for now: their
silhouette points must not be treated as fixed cross-view surface correspondences.
Annotation estimates have an assumed 8-pixel uncertainty, not measured accuracy.

The optimizer converged, with training p95 6.49 pixels and held-out p95 39.35
pixels, exceeding the existing 3-pixel target. An inspected projection overlay
shows large errors at some held-out eye corners. It also shows that provisional
mouth annotations need semantic review. This trial cannot establish whether the
error is primarily annotation, focal assumption, prior, or pose degeneracy.
Do not tune against these same held-out points and then call them independent.

Verification covers synthetic perspective recovery on unseen observations,
deliberately inconsistent held-out observations, and train/validation leakage.
A passing synthetic result remains UNVERIFIED for real reconstruction. No mesh
or texture was created or promoted from the failed real camera trial.

Reproduce (requires the geometry extra):

```powershell
python -m unittest discover -s tests -p test_bundle.py -v
python -m headfoundry.bundle <private-observations.json> --output <private-report.json>
```

Next: review semantic annotations, establish camera plausibility bounds and
independent additional observations, and compare camera initializations while
holding geometry/texture work back until real camera evidence is adequate.
