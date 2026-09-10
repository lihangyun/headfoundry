# Experiment 0057: authored lip height and position controls

Status: candidate `REJECT` for profile regression. No accepted source change.

Six additional graphical targets (upper/lower lip height increase/decrease and
mouth up/down) were read at the same fixed base revision. Each target header
explicitly declares CC0. Exact hashes and scope are recorded separately in
`examples/makehuman-mouth-height-lock.json`; the earlier volume lock remains
unchanged. No upstream application code or new model weights are imported.

Reuse the independent parser, source-ID mapping and fitting protocol from
0056. The single variable is the authored basis: three paired height/position
controls replace the three volume controls. Original mesh, cameras, observations,
5px residual scaling, coefficient regularization and +/-0.5 bounds are fixed.
All eight sign branches converge; selection uses the unchanged training cost.

Best controls: lower-lip height -0.121604, vertical position +0.087110 (up),
upper-lip height -0.000103. No active coefficient bounds. Maximum displacement
0.010476 template units, zero reversed triangle normals, minimum area ratio
0.93366. These checks do not prove global self-intersection freedom or anatomy.

| Fitting diagnostic | Source | Candidate |
| --- | ---: | ---: |
| Left local profile MAE px | 4.3040 | 4.4347 |
| Right local profile MAE px | 9.4491 | 9.9697 |
| Front mouth-point mean px | 4.8665 | 4.5382 |
| Left30 mouth-point mean px | 11.2925 | 10.1945 |
| Right30 mouth-point mean px | 8.7840 | 7.6290 |

All these observations are fitting inputs, not independent validation. Better
point alignment does not compensate for worse bilateral profile evidence.
Actual five-view same-lighting renders were inspected; the head still looks
generic and the result does not justify visual improvement or promotion.

Private `authored-mouth-height-v2` retains the actual OBJ, source/target metadata,
all sign-branch costs, fit report, five-view sheet and final surface audit.
The existing private fitter accepts `--height --orthants` while preserving its
old volume defaults and exclusive output directories. It validates consent,
all asset/license hashes and revision consistency before fitting. Identifiable
artifacts remain local and outside Git. All 71 tests pass.

The sequence 0053–0057 does not establish that lips cannot be reconstructed;
it establishes that repeated isolated lip modes under the current template,
correspondence assumptions and cameras have not delivered visible identity.
Next examine broader anatomical face-shape coverage and its coupling to those
observations, instead of repeatedly adjusting lip-only controls or trading
away the side profiles. Camera and complete reconstruction gates stay unmet.
