# Experiment 0029: active-bound objective audit

Status: `REJECT` candidate unchanged; bounded diagnostic evidence only.

The joint optimizer now reports each active parameter and separate training
depth/pixel robust-cost derivatives. Central differences use a 1e-6 perturbation
only for diagnosis, including immediately outside the constraint. No out-of-bound
candidate is returned and no held observation enters the derivative calculation.

Actual rerun: private `fit_depth_cameras.py --pixels --output
depth-camera-bound-audit-v1`. It reproduces experiment 0028's camera matrices,
scales, 17 iterations and held p95 8.8241627622 px exactly.

Only the right30 incremental rotation-vector x component is active: -0.1 rad.
At this point, holding all other parameters fixed:

- depth robust-cost derivative: -5.5180 per radian;
- pixel robust-cost derivative: +24.1289 per radian;
- summed derivative: +18.6108 per radian.

Thus moving this parameter farther negative locally reduces the pixel objective
but increases the depth objective. This establishes a local conflict in the
current training objective, **not** the true physical camera orientation, the
correct depth, a global optimum, or the cause of all visible seams. It does not
justify blindly expanding bounds. Rotational increments are axis-angle vector
components, not independently measured Euler pitch angles.

The depth/pixel robust costs are 10.8759 / 106.1626 with the existing respective
0.01-input-unit / 3-pixel normalizations. They are not physical error units or
an argument for tuning weights to held-out scores. The corrected depth-only RMS
is 0.00684791 before and 0.00254498 after optimization.

51 tests pass. No geometry, inference asset, acceptance threshold or baseline
changed. Next examine whether the limited shared-depth-scale model can express
the observed disagreement without forcing camera rotations to compensate.
