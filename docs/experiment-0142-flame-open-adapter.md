# Experiment 0142: FLAME 2023 Open identity adapter

Status: deterministic local adapter `TECHNICAL_CHECK_PASSED`; official asset,
subject fitting and visual result `UNVERIFIED`.

The target is a coherent 300-dimensional identity-shape prior that can replace
the exhausted local depth fields. The hypothesis is that the separately named
`FLAME 2023 Open` model provides a commercially usable shape space under
CC-BY-4.0. The counter-hypothesis is that an old/non-commercial FLAME file,
ambiguous source, modified archive or malformed geometry can enter the pipeline
under the same name. This experiment changes only the model asset/neutral
identity decoding path; cameras and subject geometry remain untouched.

The local NumPy adapter accepts exactly `FLAME-2023-Open`, the official FLAME
source URL, `CC-BY-4.0`, a recorded official-source digest and a separately
locked safe NumPy conversion. It requires attribution, review identity/date,
commercial-use acknowledgement, change disclosure and review of the published
prohibited uses. Standard FLAME releases, non-commercial texture assets,
unknown conversions, missing records and digest drift fail closed.

A deterministic four-vertex fixture verifies all 300 identity coefficients,
neutral linear decoding and unchanged topology. Negative tests reject an old
model identity, research-only license, false commercial-use record, unknown
conversion, malformed source digest, converted-file tampering, a 299-direction
archive, floating-point face indices and invalid/out-of-bound coefficients.
These tests establish the contract only; they do not establish compatibility
with bytes that have not been downloaded or subject likeness.

The official download currently requires account sign-in. No official archive
is present locally, so no source digest, real topology count or real identity
fit is claimed. After the exact `FLAME2023Open.zip` is downloaded locally,
inspect its contents, record the hashes, convert only `flame2023_Open.pkl` to
the safe neutral archive, and rerun the adapter before any subject experiment.

