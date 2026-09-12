# Experiment 0099: bounded candidate mouth review

Status: `UNVERIFIED`; not promoted as a natural closed-mouth reconstruction.

Audit the actual exported 0098 candidate, not the earlier pair-only mesh.
Thirteen lateral sections contain zero proper 2D crossings in source and
candidate. This still excludes tangencies, collinear overlap and unsampled 3D
intersections; full collision freedom remains unverified.

Recomputed mouth-only profile means improve from 4.618532/8.928231 to
4.497605/7.633857 px. Enlarged front/oblique photo-versus-clay overlays were
rendered and inspected with all six original mouth samples marked. The opening
remains evident and the lip shape is angular; internal half-gap fitting has
not produced the photo's closed visible seam. The original lower seam sample
14 is occluded in all three views. This does not alone prove invalid contact,
but prevents treating its projection as a visible image landmark.

The actual support audit uses the candidate's exported camera array and logs
its own hashes. Serialization changes NPZ bytes, so its hash differs from the
source file even though it contains the copied matrices. No source camera is
silently substituted in the overlay.

Decision: do not keep reducing internal pair distance as the sole mouth goal.
The next fitting objective needs the visible photo lip line and corresponding
apparent model seam with view-specific visibility, alongside contact safeguards.
The current candidate remains experimental; source/defaults stay unchanged.
Private `rim-bounded-section-audit-v1` and `mouth-support-bounded-v1` retain
actual profile/crossing checks and enlarged overlays. No personal data is
committed. Public production code is unchanged.
