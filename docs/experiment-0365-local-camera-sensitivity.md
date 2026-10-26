# 0365 frozen-evidence local camera sensitivity

2026-10-26. Diagnostic only under updated task contract; no model restoration,
patient access, nonlinear refit, output promotion or old threshold change.
Compare saved0332initial geometric state and archived0363state using their own
unchanged admitted/train populations. Different populations mean no controlled
model ranking. Known scene truth is evaluator-only, never a reconstruction seed.

At true cameras/XYZ in the same identity-anchor/unit-baseline gauge, form the
existing analytic residual Jacobian. Check every column against centered finite
differences step1e-6; max abs difference/(1+abs numeric)<=1e-5. Repeat derivative
check at each saved fitted state. No alternative step/tolerance on failure.
Project log-focal derivative orthogonally away from all nuisance pose/XYZ columns
(column-normalized NumPy lstsq,rcond1e-12). Report remaining focal information,
linear predicted logf error from actual observation residual, recorded logf error,
and per-observation signed contributions. This is local unweighted sensitivity,
not the nonlinear soft-L1 solver, causal uniqueness or a new fitted camera.
Exact-zero residual must predict zero; injected0.001logf derivative must recover
0.001 within1e-8. No source-ID pruning, weights, confidence or frame changes.

One bounded worker60s/2GiB, existing NumPy/OpenCV/shared helpers. Save complete
small report and contribution arrays. Stop on identity/finite/derivative/control
failure. If checks pass, distinguish implementation agreement from geometric
accuracy; no automatic move to head fitting or archived model replay.

## Result

Source0d97d1f. One worker1.703s,104448000B conservative process-tree peak,exit0.
TECHNICAL_CHECK_PASSED diagnostic only;0363REJECT and all real-head gates unchanged.
All columns tested at true and saved states. Worst derivative normalized error:
0332true4.131e-8/fitted2.990e-8;0363true4.800e-8/fitted9.125e-8, below1e-5.
Exact-zero and injected logf controls passed. No alternate tolerance or rerun.

| Quantity | Successful0332 initial | Failed0363 |
| --- | ---: | ---: |
| Training points |69|75|
| Observation component RMS at truth,px |0.114699|1.478733|
| Raw logf derivative norm |4698.239|4641.487|
| Logf derivative norm after nuisance projection |116.335|110.011|
| Local unweighted predicted logf deviation |+0.000454415|-0.016925729|
| Recorded nonlinear logf deviation |+0.000464354|-0.011016565|

Most raw focal sensitivity can be expressed by pose/XYZ variation; orthogonal
remaining sensitivity is small relative to the raw norm in both cohorts.
This is gauge-specific local coupling,not proof of global degeneracy or a
calibrated uncertainty interval. The derivative checks give no evidence for a
Jacobian implementation error at these states,not universal software correctness.

0332linear prediction closely matches its observed deviation.0363linear forecast
has the same sign but materially different magnitude; nonlinear soft-L1 loss,
finite displacement and other factors have not been isolated. Thus observation
errors plus local geometric coupling plausibly account for focal bias without
requiring an incorrect derivative. They are not a uniquely established cause.
The populations differ,so this is not a matched detector-quality ranking.

Next-design constraint: a lower residual or simply changing optimizer does not
address the measured issue. Seek independently supported correspondence precision
and/or additional calibration information. Photometric refinement is a retained
conditional capability from0332,not automatic permission to reuse0363as a seed:
0363also has four true visibility misses,which a focal correction cannot itself
erase. No post-hoc removal of those IDs is allowed. Model-download/refit/parameter
sweeps remain prohibited without a materially different preregistered mechanism.

Complete small evidence:assets/private/camera-sensitivity-0365/result.json,
contributions.npz,worker.json,worker.log. No generated mesh or failed runtime
was installed; the diagnostic checker is retained as successful evidence tooling.
