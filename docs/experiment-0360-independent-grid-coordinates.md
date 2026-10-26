# 0360 independent feature-cell coordinate contract

2026-10-26. Software-only continuation after732/732strict weight load0359.
No vendor coordinate implementation copied/imported; derive from rectangular
grid geometry: row-major index i, width/stride columns, midpoint of each stride
square gives x=(column+.5)*stride,y=(row+.5)*stride. Units are pixel-edge units,
consistent with normalized x/width*2-1 and align_corners=False sampling used
in the inspected inference code. This mathematical consistency is not proof of
the trained checkpoint's label convention; no offset sweep to fit observed data.

Single declared convention, no alternative tuned after viewing predictions.
Owned2x3grid exact centers, empty-shape preservation, five invalid inputs and
feature-center sampling test; <=30s/1GiB, no model weights/forward or patient data.
Next full-forward experiment must measure actual prediction errors with fixed
known coordinates, not assume this small arithmetic check proves them.
0359 historical load-only result remains unchanged; current local helper gains
this explicitly specified independent implementation. Nonzero DropPath still
fails closed. Main source/defaults and all3px/2mmphysical gates unchanged.

Actual arithmetic control passes: exact expected centers,5/5invalid cases
rejected, feature sampling maximum difference5.960464477539063e-8. Command
elapsed5.676s. This small command was invoked directly rather than through the
process-tree monitor; peak memory was not measured, so the proposed1GiB bound
is NOT independently certified. No actual model inference occurred. Evidence:
assets/private/trackon-coordinates-0360/controls.json. Existing generated0359
private helper remains its original load-only copy until explicitly regenerated
for a separately registered forward check; no implicit deployment.
