# Experiment 0006: licensed automatic landmarks

2026-09-05. Real camera result REJECT; full reconstruction UNVERIFIED.

Google's official FaceMesh V2 model card specifies Apache License 2.0:
https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Face%20Mesh%20V2.pdf
The official task guide links the pinned version-1 model bundle:
https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker

Bundle URL:
https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

SHA-256: `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`.
The local CPU task detected a face in all five consented images. The card
specifically warns against views beyond 80 degrees, so the profile predictions
are excluded from the camera experiment. Detection does not establish accuracy.

Reusable command (requires MediaPipe, Pillow, NumPy installed in the runtime):

```powershell
python tools/detect_face_landmarks.py <private-run-manifest.json> <face_landmarker.task> <new-private-output.json>
```

It checks local consent, input hashes and the pinned model hash before inference,
keeps the original files, and refuses to overwrite an existing observation report.

Twenty landmarks from the frontal and intermediate images were supplied to our
perspective bundle solver. The frontal prediction supplied an approximate depth
prior, so no frontal observations were held out. Eight observations from the
two other views were held out, with at least two training views per landmark.
Intrinsics remain assumed, not measured. The single primary change is observation
generation, replacing approximate manual annotations with a licensed detector.

Result: optimizer converged, training p95 1.69 pixels, held-out p95 16.93 pixels.
This fails the 3-pixel camera gate. It is not directly comparable as an improvement
percentage against experiment 0005: the points and split changed. Detector
predictions are correlated learned estimates, not independent scan ground truth.

Review of experiment 0005 also revealed frontal validation leakage: its prior
was constructed using all frontal observations, including the held-out ones.
That experiment's reported holdout figure was therefore not fully independent.
The bundle input now supports declared prior-source views and rejects overlap
with validation views. Callers must provide honest provenance; this check cannot
infer undeclared dependencies.

Next: enforce camera and shape plausibility, inspect predicted correspondence
locations, and establish side-view observations independently. Do not fit a head
to compensate for a failed camera. The goal remains a complete editable textured
head and visual evidence on real photographs, not detector landmark agreement.
