# Experiment 0055: pinned anatomical mouth target assets

Status: asset parsing/mapping `TECHNICAL_CHECK_PASSED`; subject fit and visual
quality `UNVERIFIED`. No new accepted head, camera or training model.

After the limits of ad hoc lip modes, inspect the existing template's graphical
shape targets. The [pinned official license, section C](https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.md)
explicitly includes targets/modifiers in CC0 graphical assets, separate from
program logic. Each of the six selected files also declares its CC0 release
in its header. This does not extend to unreviewed third-party assets.

Selected only increase/decrease pairs for lower-lip volume, upper-lip volume
and philtrum volume from the official `makehuman/data/targets/mouth` directory
at the same fixed revision as the base mesh. Each exact SHA256 is recorded in
`examples/makehuman-mouth-target-lock.json`. No application implementation,
training data, paid model or alternative checkpoint is imported. GitHub's
anonymous API listing was rate-limited; the public repository directory and
raw graphical assets were inspected without credentials or API retries.

`parse_target` is a small independent sparse displacement parser: source vertex
index and three numeric offsets, comments allowed, unspecified vertices zero.
It rejects duplicate/out-of-range indices, nonfinite data, malformed rows and
empty targets. It does not itself grant rights or infer matching topology.

The preparation entry point verifies both target and base/license hashes and
matching revisions before parsing. It maps the 19158-vertex base indices to the
4459-vertex head crop, applying the same rigid y/z-axis conversion to offsets.
The six targets affect 59,130,25,15,95,141 head vertices respectively. No source
IDs are guessed from geometry proximity. NPZ output retains names, topology,
source vertex IDs and deltas. Actual execution and all 71 tests pass.

Reproducible preparation (from repository root):

```powershell
C:/Python313/python.exe -m tools.prepare_makehuman_targets assets/private/makehuman-base-v1 assets/private/makehuman-mouth-targets-v1 assets/private/makehuman-mouth-basis-v1
```

Output creation is exclusive; do not rerun against an existing output directory.
Original asset files are retained outside Git; the lock and importer are tracked.
The verified asset files must be installed before running, with no network
fallback or silent noncommercial substitution inside the importer.

Inspected actual front/oblique renders of the generic base and each target at
unit strength in `makehuman-mouth-basis-v1/target-preview.png`. The intended
volume differences are visible. Unit extremes are not automatically suitable
for realistic subjects, and topology alone does not prove anatomical accuracy.
No deformation has yet been fitted to the five photos with these assets.

Next map these same source IDs through the experimental neck clip and fit a
bounded small combination against multi-view observations, checking both
profiles and frontal landmarks. Unlike frontal-ray modes, these assets can
change frontal geometry; that effect must be measured, not hidden. Preserve
the pre-dense source and keep all acceptance gates in force.
