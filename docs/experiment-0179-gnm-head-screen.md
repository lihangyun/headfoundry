# Experiment 0179: Apache-2.0 GNM Head prior screen

Status: official source/model lock and local neutral-mesh execution
`TECHNICAL_CHECK_PASSED`; subject identity fit `UNVERIFIED`; direct template
substitution and default promotion `REJECT`.

The [official GNM repository](https://github.com/google/GNM/tree/5482149067eda4bf9d423398fe29c4436f936f10)
states that its ecosystem is Apache-2.0 and commercially usable. The
[GNM Shape README](https://github.com/google/GNM/blob/5482149067eda4bf9d423398fe29c4436f936f10/gnm/shape/README.md)
places the model data within the repository; the checked-out `LICENSE` is
Apache-2.0. A private local checkout is pinned to commit
`5482149067eda4bf9d423398fe29c4436f936f10`; its v3.0 `gnm_head.npz`
is SHA-256 `785d62572590b1073d3f93c61d82346c1e33ffacd3f8245a1b6e0b33cf59e13d`.
This is a source/model-rights screen, not a claim about rights in upstream
training scans or permission to redistribute a future combined product
without its license notices.

The NumPy model archive supplies 17,821 mean vertices, 35,324 triangles and
253 identity directions. Only the mean was evaluated. Its neutral mesh was
converted to the project's coordinates, then a **two-parameter vertical
similarity only** was fitted to provisional MediaPipe nose/chin detections
from the five authorized photos under fixed, unaccepted cameras. The fitted
vertical scale is 8.931 and translation 2.577 model units. Remaining
nose/chin pixel errors are front 10.34/2.43, left30 5.64/10.83,
left90 4.18/25.15, right30 1.59/10.44, right90 11.81/14.91.

Actual five-view neutral renders show more coherent generic ear and neck
anatomy than the current open/patchy head, but the face is not the subject,
and the test has no hair or photo appearance. These same-photo detections
are not independent validation. The mean cannot replace the current result.
The model is a legally viable *candidate identity basis* to fit and screen
under bilateral profile/eye/mesh protection; its actual benefit remains
unproven. Do not add TensorFlow or other broad upstream dependencies merely
to screen it: the current NumPy archive and renderer suffice.

The local checkout, subject renders, detections and derived data are ignored
and were not uploaded. No camera, full-head, texture or KeenTools-quality
claim follows.
