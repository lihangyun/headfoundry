# 0348: one fixed LingBot physical camera prediction

Registered2026-10-24 after0347strict-load pass,before any forward prediction.
Whole30minutes;one inference worker180s/16GiB RAM,one evaluator60s/1GiB.
No training,patient data,scan,case002 or package changes. Existing0332owned
three native720x1280PNG images in order0,1,2,hashes in its inputs.json.
Input sheet reviewed:20textured planar rectangles on black background,not
natural skin. Known nontrivial camera geometry makes this a conditional
physical probe; it is not medical accuracy or general-domain validation.

One main variable versus the successful0332camera result: replace its DIS/
bundle/direct estimator with frozen LingBot camera/depth prediction. No reuse
or restoration of retired matching integrations. Fixed0347checkpoint/source,
SDPA,BF16aggregator,FP32heads,4iterations,KV64;initial scale frames3,
keyframe interval1,upstream518crop,no warmup/compile/rerun/precision changes.
Only three image bytes,source and checkpoint enter prediction. Truth/queries
are loaded solely by the evaluator after saved immutable predictions.

Score all96original source queries with known3D,not the86DISselected matches.
Before scores,define supported population as true projections inside all
three crop supports (1pixel margin);publish exact IDs and all excluded IDs.
This reflects actually supplied field of view,not confidence/error filtering.
Save raw full predicted camera/depth/confidence; never threshold confidence.
Evaluate native predicted K and W2C using adapter from0347.

Gauge only: anchor camera aligns orientation/origin; a single positive scale
minimizes squared camera-center displacement error across both other views.
No per-view pose correction or focal/shape fit. Then project fixed trueXYZ
through each predicted native camera. Require finite proper poses,positive
depth for every scored point,each-view p95<=3nativepx,and nativefx/fyrelative
errors<=2% against knownK. Save all errors plus center/rotation residuals.
Independent truth projection must replay stored truth_uv within1e-7px;
evaluate ground-truth cameras through the same alignment for a zero control.
Failure closes this fixed prediction recipe;no frame/crop/count/threshold/
precision rescue. It does not prove all natural-video predictions impossible.
No head fitting proceeds from a failed camera result. Preserve compact raw
predictions/errors/source and cleanup exclusive failed integration before
choosing any different route. Actual human3px/2mm/visual gates remain open.
