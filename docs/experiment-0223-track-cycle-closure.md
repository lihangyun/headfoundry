# Experiment0223: anchor-cycle consistency before frozen-3D localization

Date:2026-10-19. Pre-registered before cycle measurements. Status:`REJECT`.

0222's reference replay passes but held pixel rigidity fails. Test one different
observation mechanism: detect accumulated temporal drift by comparing the saved
multi-step track with a direct reference612->target track. Freeze0221's model,
intrinsics, every existing pose gate and the unchanged0220 LK implementation.
No scan, new3D optimization, source-camera adjustment or parameter sweep.

Track all245 reference points directly to each exact-identity held image using
the original forward/backward LK check (<=0.75px) and patch-error check (<=15).
Join IDs with the corresponding saved0222 temporal observations. Require direct
and sequential endpoints to agree within0.75px, reusing the existing tracking
uncertainty threshold. Eligibility is computed without3D residuals or pose.
Use the direct endpoint for pose/evaluation on the original even/odd IDs. Report
every eligibility count and endpoint-disagreement distribution, including those
that fail. Do not introduce residual-based validation filtering.

Run the same EPNP/refinement and all gates from0222 exactly once. >=30 points in
each split, >=30 training inliers, validation spread>=50px each axis, proper
rotation, positive whole-cloud depth, validation p95<=3px both frames remain
required. Failure stops this configuration; no threshold/mask/flow-scale sweep.
Time budget60s. Original outputs and source hashes must remain unchanged.

The frames have already been inspected: any pass is a development consistency
check, not a fresh held-out result. Closure can miss a consistently wrong match;
retained patch evidence must be reviewed, and camera, scan, complete-head and
reserved-case acceptance remain separate required gates. Case002 stays reserved.

## Single-run results and stop

| Frame | Direct LK valid | Sequential survivors | Both paths valid | Closure accepted | Train / validation |
| --- | --- | --- | --- | --- | --- |
|624|86|243|86|58|28 /30|
|1040|59|102|31|0|0 /0|

Both frames stop before pose fitting at the fixed>=30 points per split gate.
Do not lower the gate to28, increase closure tolerance, change reference frames
or try flow pyramid/window sweeps to rescue this configuration. Actual accepted
point overlays were inspected; the later frame has no retained supports.

The endpoint disagreement for **valid direct and sequential** observations has
p50/p95=0.462838/2.868097px at624, and12.043683/29.591297px at1040. The raw archive
also includes invalid direct estimates; its all-candidate p95 values115.92/84.55px
are not a valid-track drift estimate and must not be cited as one. This exposes
path disagreement, not proof that either path is anatomically correct. A
consistent wrong match could evade this check.

Original model hashes remain unchanged. Private controls, cycle arrays,
`report.json` and `cycle-review.png` preserve the stopped result. No camera or
head is promoted. Freeze this chained/direct LK observation family here.
Next consider the already locked Apache-2.0 XFeat/LighterGlue matcher on the real
video, where direct cross-frame appearance associations can establish long-range
constraints rather than inheriting an unverified accumulated track identity.
Historical failures on independently generated AI images do not establish its
performance on this true video; neither is success assumed. One bounded
observation preflight must precede any new mapping attempt.

Verification: `python -m unittest discover -s tests -v` passes147 tests in4.415s.
New tests check disjoint validation/pose fitting, essential-fit isolation,
known synthetic cameras and ID-preserving cycle eligibility. Tests prove the
implemented controls, not physical camera/head accuracy.
