# 0354 authorized diagnostic replay

User explicitly approved "允许诊断回放" on2026-10-25. Goal card still blocked;
this is the separately authorized diagnostic, not a goal-status override.
Use ponytail: existing OpenCV/NumPy and bounded_process, no dependency installs.

Before execution: one worker <=180seconds/2GiB; exact0352 archive, observations,
13/9partition, thread4/RNG331/f1280/Essential1.5/.999 and ordinary recoverPose.
No seed/configuration sweeps, no optimizer/direct fit, model, video decoding,
scan, head or medical score. Stop at the same original support rejection.
Only add logs: E/input/output masks, selected pose and all four decompositions,
per-point depths, positive and positive-with-depth<50 counts. Compute diagnostic
counts independently and require agreement with actual API return. No second
recoverPose call with changed distance. Diagnostic success means records agree,
not that reconstruction passes. Original0352 REJECT remains unchanged.

Keep compact full diagnostics/hashes and Git source; retire one-shot replay
runner when finished, preserving shared contract test and original assets.

## Actual diagnostic

Source38738c1. One worker1.391seconds,105238528bytes conservative tree peak,
exit0. Diagnostic TECHNICAL_CHECK_PASSED; reconstruction remains REJECT.
Same first pair (source240,target300) stops; second pair not executed.
Essential inliers11 of13 training points. Four candidate positive-inlier counts
[2,0,9,0]; near-positive counts[1,0,6,0]. Selected candidate2 has9 positive
inliers,3 of which fail distance<50, giving actual API support6. Independent
counts match API. At least10 of11 would be needed for the original90% rule;
even the best pure-positive count9/11 (81.82%) fails. Thus far-depth filtering
contributes but cannot alone explain/rescue the failure. No threshold experiment
was performed. This is not proof that input correspondences are incorrect:
wrong focal, noisy matching/nonrigidity/degeneracy remain unseparated hypotheses.
No current evidence warrants a same-route threshold or seed retry.

Full per-point depths, candidate points, E, K, masks, selected R/t, observations,
source IDs and exact split saved in assets/private/pose-diagnostic-0354.
diagnostic.npz SHA256
b3f99fdd5f66580bd5b80aecc4b97c727d392f5269ead8ace8d4d509132abb90;
result.json SHA256
9fe07b1158b503f121a8d37495ccf925484da64aa253d35de3fbbcc207873f1e.
Keep both plus worker.json/worker.log; no model or environment acquired.
