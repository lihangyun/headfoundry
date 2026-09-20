# Experiment 0133: mouth-depth smoothing

## Question

Can screened graph smoothing remove experiment 0132's sharp lip form while
preserving its bilateral contour gain? Freeze the 0132 cameras, topology and
raw displacement. Smooth only the scalar frontal-ray depth field inside a
fixed mouth ellipse, with the raw displacement outside the ellipse as the
boundary condition. Sweep one strength from 0 to 30.

Dense profile traces are divided by row parity after excluding the sparse rows
used by prior fits. Even rows select strength; odd rows are withheld from this
sweep's selection. Both subsets still come from the same photographs and trace
procedure, so this limits current-step leakage rather than providing independent
identity validation.

## Result

The selected strength is zero. Every nonzero strength worsens both dense
selection and audit evidence. At strength 0.03, mouth depth edge energy falls
from 0.046101 to 0.044955, but selection p95 changes from
13.373/16.563 px to 13.406/16.579 px and audit p95 from
13.617/16.340 px to 13.654/16.356 px. Sparse profile means also worsen from
3.624/4.923 px. Strengths 0.3, 1 and 3 introduce relative normal reversals;
larger smoothing continues to trade contour fit for lower graph energy.

Execution and the evidence split are `TECHNICAL_CHECK_PASSED`. All nonzero
smoothing is `REJECT`; experiment 0132 remains unchanged. The angular lip is
not high-frequency noise that can be removed by graph fairing. Do not repeat
this smoothing sweep or promote lower Laplacian energy as anatomy.
