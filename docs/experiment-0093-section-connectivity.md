# Experiment 0093: ordered section connectivity

Status: `TECHNICAL_CHECK_PASSED` for curve ordering; anatomy `UNVERIFIED`.

Add `section_paths` to connect section endpoints while preserving their
segment/endpoint references, hence their triangle barycentric support. Coincident
endpoints merge within explicit tolerance; duplicate edges collapse. Reject
branching, degenerate segments and ambiguous endpoint merging rather than
silently choosing an anatomical path. Closed paths repeat their first point.

On the actual supported lip section from 0092, the 61 segments form two
unbranched paths with 30 and 33 points. These follow the sliced exterior/inner
surfaces and are not yet the transverse upper/lower lip rims. Do not confuse
successful connectivity with anatomical selection or a contact-ready model.
The existing mesh and camera remain unchanged.

Tests cover disconnected paths, shuffled/reversed edges, duplicates, a closed
loop, branches, degenerate segments and empty input. Full suite: 81 tests pass.
Next identify surface turning locations on these ordered paths across lateral
sections, inspect them on the actual head, and only then build rim constraints.
