# 0370 frozen distance sensitivity audit

2026-10-27 preregistration. Diagnostic only; no optimizer, model or patient.
Read original0367/0369inputs and stored0368/0369solutions. First40points,
unchanged fixed stress. Evaluate analytic four-parameter Jacobian at truth;
check each column against central differences1e-6, normalized maxerror<=1e-5.
Compute local response -lstsq(J,residual) for fixed pixel-only,depth-only and
combined perturbations. These are attribution diagnostics, not candidate fits;
do not promote predicted parameters or use their results for tuning.
Report normalized singular values, focal column after nuisance projection,
predicted versus saved actual logf shift and nonlinear remainder. Exactzero
and injected .001*J[:,0] controls must produce0 and-.001 logf response.
One60s/1GiB worker. This distinguishes local error propagation from gross
solver failure without claiming a unique cause or independent noise statistics.

## Findings: technical audit passed; camera admission unchanged

Sourcef669b87,one worker.500s/45293568B conservative process-tree peak.
Analytic-vs-central-difference normalized errors<=8.99e-10; zero and injected
column controls pass. No camera optimization or patient access occurred.

0368 local predicted logf: pixels-.00623729,depth+.00720333,
combined+.00102424; saved actual-.00259932,remainder-.00362356.
0369 local predicted logf: pixels-.00959879,depth-.00787883,
combined-.01753963; saved actual-.02193728,remainder-.00439765.
The successful fixture has opposing local contributions; the failed one has
reinforcing contributions. Nonlinear remainder is material, especially0368
where even the sign changes, so these are not exact causal percentages.

Normalized Jacobian minimum singular values .01636699/.01889287;
nuisance-projected focal norms20.63636/21.59908. The failed case is not simply
more locally ill-conditioned by these two measures. Larger error is consistent
with perturbation direction coupling, not evidence of a broken optimizer.
One deterministic pattern says nothing about a real depth model's bias law.
Neither small raw residual nor optimizer success can certify the3px gate.

Implication for combining strengths: retain physical constraints and correct
noiseless capacity, but do not treat all pairwise squared distances as equally
reliable independent observations. Pairs share points and therefore share
measurement errors. A genuinely different candidate is a pixel/depth
measurement-space errors-in-variables objective, with explicit noise scales
and latent points, rather than retuning this distance recipe. Its advantage
is still UNVERIFIED; real noise scales must not be invented from scan truth.
Before implementation, inspect shared geometric backend and preregister an
ablation on these same frozen fixtures, heldout unchanged, fixed budget and
stop rules. No model installation or head fitting is justified yet.

Result retained locally: assets/private/distance-sensitivity-0370/result.json,
SHA256077d9d2329b1704679e66867c7502843d3d408e8239864749b27cdd4ce4f5be1.
Both original input files and historical results unchanged; diagnostic runner
is retained as successful audit evidence, not a revived failed camera runner.
