# Experiment0267: native dense motion on the actual video

Date:2026-10-20. Goal active;0266 is closed and cleaned. No head is accepted.
Register before executing any candidate tracking. Start10:10:41Z,end10:40:41Z.

## Hypothesis and main variable

Dense Inverse Search (DIS) uses spatial propagation/patch mean normalization and
variational refinement,unlike the retired independent sparse pyramidal LK
observation path. It may preserve more useful observations under native small
video steps. Counter-evidence:regularization can create coherent wrong motion,
and cycle closure cannot prove anatomical correctness. This tests readiness,
not camera/head acceptance. No retired framework/weight/script is restored.

Use already installed OpenCV5.0.0/NumPy2.5.2,CPU4threads,DIS MEDIUM unchanged,
forward/backward independent fields without supplied initial flow. OpenCV is
permissively licensed;no trained weights/download/training/upload. Primary
references:[DIS API](https://docs.opencv.org/4.x/de/d4f/classcv_1_1DISOpticalFlow.html)
and [OpenCV license](https://github.com/opencv/opencv/blob/4.x/LICENSE).

Only authorizedcase001 video is selected before manifest validation. Decode all
1041 native720x1280 frames sequentially and require every RGB SHA to equal0252.
Never open skin/bone/case002. Keyframes are every12 native ordinals plus1040;
unlike legacy seeked endpoints,all ordinals have their literal decoded meaning.
This is not a matched-input causal comparison to old0220's frozen image set.

Use the same conservative face-interior cue as the historical video work:
R-B>12,ROI[100,500,620,820],largest connected component,8x8 erosion. It is not
accepted skin segmentation. Seed up to400 Shi-Tomasi points (quality.01,
distance5,block7),excluding5px around active tracks. Propagate using dense-field
bilinear samples;require image bounds,finite fields,bidirectional error<=.75px
and target cue membership. Save all retained/ended IDs/counts,no3D residual filter.

## Fixed readiness gates and limitations

At least80% adjacent keyframe pairs share50 IDs;one common-track component must
contain80% keyframes and both original profile intervals120..168/396..444.
At612 save all current IDs. For624/1040 compare sequential endpoints with direct
DIS612->target and reverse fields. Report the entire both-valid disagreement
population before closure filtering. Require its p95<=3px,then endpoint closure
<=.75px,at least30 IDs in each parity split and50px span in both axes. These are
consistency/readiness checks,not ground-truth pixel error or a camera pass.
Do not report a tautologically filtered p95 as independent accuracy.

First a deterministic synthetic translation/control must pass:p95 position
error<=1px and all source arrays finite. Five invalid/bilinear/identity checks
must pass. No threshold,preset,reference-frame,mask or sampling sweep. Even a
positive readiness screen still needs independent physical correspondence and
3px camera evidence before head fitting;medical2mm/mesh/visual gates unchanged.

Implementation<=480s,one video worker<=360s,actual two-view review/report<=120s,
whole phase<=1800s including cleanup/tests/commit. No persistent raw-frame dump;
at most two necessary source/track sheets. Failed readiness stops before any
camera/head solve. Archive exact small reports/control/tracks/hashes/Git source,
then remove exclusive runner/tests/raw outputs before another route. Shared
OpenCV/main environment and all originals/successful fixtures stay. Keep0207.
