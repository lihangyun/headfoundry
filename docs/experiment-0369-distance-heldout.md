# 0369 independent held-out capacity

2026-10-27 preregistration. No change to0368fit, thresholds or initialization.
Question: does the conditional distance mechanism predict points never fitted
on a different fixed geometry/camera, rather than only its first fixture?
RNG369,60points x/y uniform[-.6,.6],z uniform[2.5,3.5];
f900,Rodrigues(-.15,.18,.06),translation(-.12,.09,.16).
Axial inputs d=z1-.3,e=z2/1.2+.2. First40fit,last20evaluation only.
Exact and one stress: .5px*sin(arange120 reshaped60x2), view2offset2;
depth .005*sin(arange60+4/6). No sweeping or retrying.
Exact: focal relative<=1e-6,held transformed-point p95<=1e-6sceneunit;
stress: focal relative<=.02,both held true-point projection p95<=3px.
Require0368admission and positive held predicted depth. Report rotation,
translations,shifts,training and held errors; do not confuse scene units with
medical millimetres. This is not a proof for all geometries or real depth maps.
One60s/1GiB worker, source committed before execution, no assets installed,
no human inputs. Failure stops this transfer test; retain0368conditional
success,archive0369result and retire only this exclusive runner if failed.
Success advances toward real-component input assessment, not head fitting.
