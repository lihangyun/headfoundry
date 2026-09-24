# Experiment 0180: GNM identity-basis profile transfer

Status: pinned local 30-PC neutral GNM evaluation and exact raster comparison
`TECHNICAL_CHECK_PASSED`; this candidate's bilateral profile and visual
promotion `REJECT`. The GNM asset itself is not rejected as a whole.

The Apache-2.0 GNM Head v3.0 archive pinned in experiment 0179 was the only
new shape source. The five existing cameras and photographs were unchanged.
The experiment used its first 30 identity directions and ten semantically
paired official 68-point facial anchors (chin, nose tip, four eye corners,
mouth corners and inner lips) against provisional local MediaPipe readings.
Front and both 30° views fit the coefficients, a bounded horizontal scale
and depth translation. The 90° views contributed no identity loss in that
first stage. Training-view mean anchor errors fell from 23.31/21.04/21.79
to 6.81/6.58/6.65 px. The untouched-profile anchor means fell from
20.27/20.60 to 16.50/11.04 px, but the actual faces still looked generic.

A second stage added alternating rows from *both* pure-profile facial
traces, retaining the other rows for transfer checks. The selected fit uses
horizontal scale 9.478 versus the original neutral screen's 7.0, a large
35.4% stretch that cautions against treating this as a calibrated identity.
Maximum vertex displacement from the neutral screen is 0.309 model units;
minimum triangle-area ratio is 0.888 and no face normal reverses. These
are mesh-safety checks, not identity checks.

The exact 1254 px z-buffer, under the same cameras and at the **same frozen
photo contour rows**, gives:

| Pure profile | Current head, all rows | GNM fit, all rows | Current held rows | GNM held rows |
|---|---:|---:|---:|---:|
| left90 | 4.24 px | 6.53 px | 5.50 px | 7.50 px |
| right90 | 4.94 px | 7.00 px | 5.00 px | 8.13 px |

Thus the fitted GNM candidate loses to the current head on *both* sides,
including every withheld-row aggregate. The private same-camera sheet
places source photos, current clay and GNM clay side by side at front and
both profiles. GNM has a more complete generic ear/neck surface, but its
facial identity, jaw/lip relationship and overall photographed hairstyle
remain wrong. Do not replace the current head or add photo color to hide
this geometry deficit. Simply adding more unconstrained PCA directions is
not justified by the held-row and visual result.

The holdout is limited: these rows were not in the second-stage objective,
but are from the same photographs; earlier camera estimation, vertical
template alignment and current-head development had used these views.
The detections themselves are provisional. This does not establish
independent reconstruction accuracy or the ceiling of the full GNM model.
All subject-derived reports, geometry, overlays and comparison sheets stay
ignored locally and were not uploaded. The camera and full-head visual
gates remain open.
