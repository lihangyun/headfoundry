# Experiment 0162: local bun-volume proxy

Status: independent bun geometry/render path `TECHNICAL_CHECK_PASSED`;
side-volume evidence `PARTIAL_SUCCESS`; full-head/default promotion `REJECT`.

The corrected experiment-0161 views expose a missing large side feature: the
subject's tied bun. This experiment changes only an added hair-volume
component; the experiment-0132 head vertices, topology, cameras, lighting and
five authorized local photographs remain fixed. A single closed ellipsoid is
placed from the two pure-profile bun centers, with axes approximated from
their visible extents. It contains 642 vertices and 1,280 triangles. The
source head is appended byte-for-byte to the private candidate OBJ.

The corrected Blender renderer verifies source-coordinate agreement and
subpixel camera projection before producing separate clay and photo overlays.
The component appears behind the head in both pure profiles, stays hidden in
front, and does not change face geometry or the existing profile scores.
Within preselected side bun regions, a simple dark-hair mask (mean RGB < 80)
has intersection-over-union 0.610 left and 0.552 right against the candidate's
full projected geometry; the bald baseline has zero projected coverage in
these particular regions. The isolated ellipsoid scores 0.608/0.544. This is
evidence of missing *volume support*, not a validated hair segmentation or
KeenTools-quality reconstruction. Hair strands, scalp and the neck are not
measured by these two ROIs.

Five-view inspection rejects the ellipsoid as a usable hairstyle. It looks
like a separate smooth ball beside the head in the oblique view, lacks a
scalp/bun connection and does not reproduce the pulled-back hair mass. No
texture or material was added, and no candidate was promoted to the default.
The next hair experiment needs a continuous scalp-to-bun volume with a
five-view silhouette and appearance check. Facial identity and accepted
camera/quality gates remain separate unresolved requirements.
