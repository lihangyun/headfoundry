# Audit0271: isolate coarse-pair and batched fine-window index contracts

Date:2026-10-21. Registered after0270 retirement372ffcb and before this numerical
audit. Budget10min from01:05:28Z through01:15:28Z. No model installation, weight,
private input, neural execution, scan, training or upload.

Hypothesis: two concrete indexing hazards in the frozen HF port can be reproduced
independently of learned weights. Main variable is index identity preservation
through converting an unbatched pair matcher to batch/padded arrays. Do not fit
coordinates, sweep thresholds or restore the failed inference integration.

Compare only reviewed HF source8cb5963cc22174954e7dca2c0a3320b7dc2f4edc and the
historical pre-PRL author sourceffd4a4644064354468eb1f0c7a3e732233cb732f. That
author license remains Apache2 as recorded0269;reading public source does not
adopt current PRL code or require registration. No third-party implementation
is installed. Use independent NumPy numerical witnesses, not model outputs.

1. Embed a three-cycle among valid interior tokens of a9x9 coarse grid. Apply
   fixed .2 threshold,2-token border and mutual maxima. Require explicit selected
   row/column pairs to match all three true edges. Demonstrate that the HF
   column-argmax/row-argmax same-ordinal construction does not preserve them.
   Identity and empty controls must be handled without inventing pairs.
2. Fine window is8x8 with coordinates[-3.5,3.5]. Add batch and match dimensions,
   two batches and81 candidate slots. Fixed deterministic window indices must
   select exactly the independently enumeratedxy cell in each case. Compare
   gathering on match-axis1 with gathering on window-axis2;invalid indices fail.

Stop on unexplained control mismatch or deadline. A positive counterexample is
TECHNICAL_CHECK_PASSED in source-contract diagnosis only;0270 remainsREJECT and
neither corrected model precision nor real3D identity/camera/head is established.
Retain only one small generic successful check/report, no speculative framework.

Do not automatically change every suspicious formula. The second-stage padded
window convention also occurs in historical native code;whether its learned
semantics should change is unmeasured. Its batch[0] selection does not affect our
single-pair batch. Neither is included in a proposed minimal port-conformance
repair. Only demonstrated coarse identity layout and batch-added gather axis
would be eligible for a separately preregistered, unchanged-weight trial.
