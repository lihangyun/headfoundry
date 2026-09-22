# Experiment 0160: actual visible facial boundary audit

Status: independent boundary measurement `TECHNICAL_CHECK_PASSED`;
suspected sparse-score failure `REJECT`; subject likeness `UNVERIFIED`.

After experiment 0159, the translucent Blender overlay appeared to show a much
larger facial silhouette error than the existing 3--5 px profile scores. The
discriminating hypothesis was that the profile scorer might choose a hidden
mesh edge rather than the actual outer boundary. No camera, mesh, photograph
or fitting variable was changed.

The unchanged experiment-0132 OBJ was rendered with the existing tested CPU
z-buffer under the exact five-camera archive. At each of the 17 left and 16
right frozen profile rows, the outermost occupied image pixel was compared to
the photograph's previously traced face contour. All rows had rendered
coverage. Mean absolute error was 4.24 px left and 4.94 px right, with p95
9.8 and 12.0 px. Local photo overlays show the red photograph readings and
green actual rendered boundary on top of each other. This independently
supports the order of magnitude of the older sparse profile scores; the
suspected hidden-edge explanation is rejected.

The result is narrow. These rows cover the **front facial outline** from brow
to chin, not the full cranium, hair, ear, rear jaw or neck; the same photographs
supplied the development contour readings. The 4--5 px numbers are therefore
not independent likeness acceptance. The exact Blender overlays still show
generic central anatomy and a visibly poor complete-head match. An exterior
contour alone cannot constrain the internal nose, lips, eyelids, cheek relief,
ear and hair boundary that dominate the remaining human-visible mismatch.

Next work must obtain reliable interior 3D/anatomical evidence and a shape
representation with that capacity, while separately checking the posterior
head and neck against visible evidence. Repeating sparse face-outline fitting
on the same rows is unlikely to create a recognizable subject head.
