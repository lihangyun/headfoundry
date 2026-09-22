# Experiment 0155: full CC0 MakeHuman face basis

Status: rights, lock and conversion path `TECHNICAL_CHECK_PASSED`; learned
identity quality `UNVERIFIED`.

The previous MakeHuman experiments used only 92 selected nose, mouth and macro
targets. This experiment expands the same pinned official revision to the
reviewed `asym`, `cheek`, `chin`, `ears`, `eyebrows`, `eyes`, `forehead`,
`head`, `neck`, `nose` and `mouth` folders. No application code, trained model
or unreviewed asset is imported.

`tools/lock_makehuman_face_targets.py` requires the exact previously approved
revision, enumerates only the reviewed folders, verifies the explicit CC0
header in every target and writes a deterministic SHA-256 lock. The resulting
public lock contains 348 target files. The existing fail-closed target adapter
then maps them through the locked CC0 base mesh to one common 4,459-vertex head
topology. Target support ranges from zero retained head vertices for two
non-head-compatible assets to more than 4,400 vertices for broad head/neck
controls; those counts are reported rather than silently filtered.

The source-rights check, complete hash lock, target parsing and topology mapping
are `TECHNICAL_CHECK_PASSED`. This is a legal, deterministic source basis for
controlled synthetic identities, not a trained model or subject result.
Identity quality, target-range safety and KeenTools-level parity remain
`UNVERIFIED`.

Next gate: pair inverse targets, exclude zero-support and expression-only
controls from neutral identity, sample bounded combinations, and reject any
synthetic head with triangle reversal or unacceptable area collapse. Only
after that generator is deterministic and safe may it train a nonlinear
identity prior. Real subject photographs remain local evaluation data and are
not training uploads.
