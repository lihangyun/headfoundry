# Experiment 0081: central-face graphical controls

Status: `TECHNICAL_CHECK_PASSED` asset preparation only; identity quality is
`UNVERIFIED`. No mesh, camera or product default changed.

Experiment 0080 showed that four coarse whole-head presets cannot supply the
missing central facial anatomy. Prepare a narrower, explicit set of graphical
controls from the same pinned MakeHuman revision and CC0 asset scope:

- paired left/right eye translation in/out;
- paired left/right cheek volume decrease/increase;
- chin height, prognathism and width decrease/increase.

The fourteen exact files come from the upstream `eyes`, `cheek` and `chin`
target directories at revision
`a8bc2d54ff0ac92e78ff71431b1023eda42bf482`. Every downloaded target was
read and contains the explicit CC0 release header. The public lock records
each SHA256 plus the base-asset lock. No MakeHuman application code, paid
model, research-only weight, inferred dataset grant or external private
service is used.

The existing target parser and head-crop source-ID mapping prepare a private
4459-vertex basis. Per-target affected-head-vertex counts are recorded in its
report; the prepared NPZ SHA256 is
`0731941249f3390396ce57300c543b07062ddb6c2a7d5303b8f25b08c0f403f4`.
Hash/license/revision mismatch fails closed before output. This technical
preparation does not establish that target semantics match the subject or
that combinations remain anatomically valid.

Next inspect symmetric combinations on the unchanged source, then fit only
those with direct multi-view feature evidence and enforce triangle/visibility
guards. Eye translation must not be inferred from detector labels alone;
cheek and chin changes require actual front/oblique/profile comparison. Do
not mix the prior rejected nose or head-shape candidates into this first test.

Raw targets, prepared basis and future identity-bearing renders remain under
Git-ignored `assets/private`. Only the auditable public lock and experiment
record are committed.
