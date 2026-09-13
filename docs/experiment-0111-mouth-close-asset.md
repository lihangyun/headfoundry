# Experiment 0111: explicit CC0 mouth-close expression asset

Pre-run status: `UNVERIFIED`. Target: a natural closed neutral mouth in actual
frontal, oblique and bilateral profile views. Prior identity, cameras, topology
and photo observations stay fixed. The only primary variable is the coefficient
of a separately sourced authored `mouthClose` displacement field, not another
lip-volume basis or pair-attraction solver.

The [official Faceunits 01 pack](https://static.makehumancommunity.org/assets/assetpacks/faceunits01.html)
publishes standalone graphical targets. Its archived metadata explicitly names
Mika Suominen as author and CC0 for `mouthClose`; target data have no license
header. `examples/makehuman-mouth-close-lock.json` pins the archive, metadata,
target and base-asset identity separately. It does not fabricate a shared source
revision between this community pack and the older base-mesh repository.

Read only the locked metadata and target directly from the ZIP; do not extract
or execute upstream application code. Reuse the existing sparse target parser
and source-ID mapping. Check generic base topology and actual transformed head
effect before treating the control as meaningful. A target name and valid
indices do not establish neutral expression or collision-safe contact.

Prediction: a small coefficient closes the visible seam without reversing
triangles, damaging the lip rim or worsening actual bilateral profile evidence.
Falsification: inversion, penetration, persistent open shelf, unrelated face
motion or profile regression. Do not fit/suppress held observations or relax
the camera gate. Initial fixed diagnostic coefficients are 0, 0.05, 0.1 and
0.25; none is automatically a candidate for promotion.

## Executed result (2026-09-13)

Final promotion decision: `REJECT` for every tested nonzero coefficient. The
authored field is loadable, but it does not provide a usable neutral mouth on
this already-deformed head. The prior head and cameras remain unchanged.

The locked archive and selected metadata/target hashes were verified before
parsing. Source-ID mapping reaches 1,972 head vertices. This verifies index
compatibility, not expression compatibility with the current fitted shape.
The actual exported meshes were rendered in all five fixed cameras, then
rendered again as enlarged mouth crops alongside the original photos.

| Coefficient | Left profile MAE px | Right profile MAE px | Reversed triangles | Minimum area ratio | Sampled proper crossings |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 (unchanged source) | 3.5891 | 7.2493 | 0 | 1.0000 | 0 |
| 0.05 | 3.3188 | 8.3505 | 0 | 0.7824 | 20 |
| 0.10 | 3.5376 | 8.7807 | 0 | 0.5658 | 30 |
| 0.25 | 3.4540 | 10.1618 | 2 | 0.0779 | 40 |

All nonzero trials regress the right profile. Maximum movements are 0.01796,
0.03593 and 0.08982 template units respectively; the latter two exceed the
recent 0.03 movement guard. Even the smallest trial, with no reversed
triangles, introduces sampled lip-region intersections. Triangle orientation
alone therefore misses a material failure of this proposed closure.

The section audit uses 25 fixed lateral planes through the cropped lip region
and tests strict interior segment crossings. It is not exhaustive 3D collision
detection: tangencies, collinear overlap and regions between/outside the sampled
planes are not certified. Zero crossings on the source do not establish a
closed, collision-free or anatomically correct mouth. The audit's machine
report stays `UNVERIFIED`; the combined visual/profile/crossing decision above
rejects promotion explicitly.

Visual inspection: small coefficients retain the angular lower-lip shelf and
unnatural profile opening; the larger coefficient introduces pinched/folded
appearance. None matches the photographed closed neutral lips. No identity,
side-profile, full-head or camera acceptance follows from this experiment.

Private evidence remains local only:

- `mouth-close-asset-v1`: four exported OBJ meshes, mapped field, full five-view
  comparison and report SHA-256
  `f6711e3f7732f0ba10b83270f336d90e468ba1241c691838d58b31024a57c7f9`.
- `mouth-close-contact-v1`: enlarged five-view comparison and section audit
report SHA-256
  `05076c94ab583019ba3e1bedd957399b78dfb61015b4ba7ea8ccce8f93321590`.

Regression verification: `python -m unittest discover -s tests -q` passes all
88 tests; `git diff --check` passes. No production reconstruction code or
default was changed, and these tests do not validate visual likeness.

Do not repeat a larger expression-coefficient sweep or adopt this asset as a
default closure. The next discriminating check is whether the same mapped
field has the same intersection failure on the untouched pinned base head;
that separates target/base incompatibility from applying an expression after
the current shape deformation. It is a geometry diagnostic, not a substitute
for the still-failed independent camera gate or a route to texture acceptance.
