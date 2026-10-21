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

## Actual result: two independent contract counterexamples

`tools/check_correspondence_index_contract.py` passes its fixed NumPy checks.
The interior three-cycle's aligned construction preserves3/3 true pairs;the
same-ordinal column/row construction preserves0/3. Identity and empty controls
pass. Across162 fixed fine-cell queries,window-axis gathering exactly equals
independently enumeratedxy (maximum difference0);match-axis gathering is wrong
for159/162. All invalid-index controls reject. No Torch,private input or model
is installed or run. This check is retained as a small generic successful
index-safety witness,not a neural implementation or failed-route integration.

Historical native fine matching uses a3D match/window/xy tensor and gather axis1.
The HF port adds a leading batch dimension,then retains axis1 on a4D tensor:
it now gathers candidate matches instead of window cells. The paired coarse
maps have a separate order mismatch. These are concrete differences from the
published pair/window contracts,not just another choice of model threshold.
No claim is made that the two fixes alone restore learned accuracy. Existing
padding convention is intentionally untouched;full multi-pair batching remains
unverified and is not authorized by this local two-batch gather check.

A later trial may preserve all learned bytes,pixels,precision,model config and
gates while changing only the two index-contract sites,using batch1 exclusively.
It must be separately bounded/registered;do not patch0270's historical outputs
or infer its corrected result. Actual correspondence,3D,rigidity,cameras and
head/medical/visual acceptance remainUNVERIFIED.
