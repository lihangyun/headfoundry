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

## Actual result:REJECT long-sequence readiness

Registratione04ac52,executed source49f56b8. Six synthetic controls pass;known
translation p95=.041937px,not physical3D evidence. One180.775s actual-video run
decodes/verifies all1041 native frames. There are88 keyframes/7909 seeded track
IDs.85/87 adjacent pairs have>=50 common IDs;the largest component is74/88
keyframes and includes both profile intervals. Raw graph readiness passes,
but graph density is not a physical-correspondence certificate.

| Development sentinel | Both-valid direct/sequence | Unfiltered disagreement p95 | Closure even/odd | Result |
|---|---:|---:|---:|---|
|624|377|2.592px|55/77|technical consistency pass|
|1040|0|unavailable|0/0|REJECT|

Reference612 has786 IDs. At1040 none survives the sequential path,although612
direct DIS associations pass the local bidirectional criterion. Therefore no
long-range identity bridge is established. This is lost persistence under the
fixed recipe,not proof those direct associations are anatomically correct or
all short tracks are unusable. No unknown pixel/3D truth error is invented.

Actual source-track sheets144/408 were inspected:marks occupy the selected
face/ear interior,not a new head output. Locations alone do not prove identity
or rigidity. Camera/head/medical-surface/visual gates remainUNVERIFIED. No scan,
bone,case002,training,upload,new asset or camera/head fit occurs. Stop this dense
sequential-readiness recipe without preset/mask/sampling/closure sweeps. Future
work needs an independently justified observation/rigidity mechanism,not more
sequential tracks merely because their graph connects.

## Completed closeout

Private archive:`assets/private/closed-experiments/0267-native-dense-video/evidence.zip`:
2423135bytes,17 members,two source-track images,CRC/member SHA verified,SHA256
`54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612`.
It retains exact observations/cycle arrays,reports/controls/review and source
recovery49f56b8;these are private failed-route evidence,not accepted observations.

After terminal-worker and exact path/reparse checks,remove five raw NPZ/PNG
duplicates totaling2525221bytes and the exclusive runner. No framework,weights
or environment was installed,so shared OpenCV/NumPy must not be uninstalled.
Original selected video SHA remains unchanged;scan/case002 bytes are not opened.
Other originals,successful fixtures,shared source/defaults and unrelated0207
remain untouched. No live Python caller remains.133 tests pass in4.738s.
The phase closes within its original30-minute budget;overall goal stays active.
Future work must establish trustworthy long-range identity/rigidity rather than
silently relaxing this failed sequential-chain contract. No new route starts
before this cleanup commit.
