# Experiment 0103: anonymous adult macro shape basis

Status: asset preparation `TECHNICAL_CHECK_PASSED`; both fitted geometry
candidates are `REJECT` for promotion. No subject attribute is inferred.

## Target and one variable

Test whether the missing high-impact identity variation is explained by broad
adult head/face shape directions absent from the current neutral MakeHuman base.
Keep the experiment-0037 `oblique-jaw-v3` source, all five registered cameras,
photo outlines, bilateral complete profile curves, reviewed canthus/mouth
anchors, renderer and geometry guards fixed. Only the shape basis changes.

Six graphical targets from the already pinned MakeHuman revision are locked in
`examples/makehuman-adult-macro-lock.json`. Each file explicitly declares CC0
and its SHA-256 is verified before parsing. The upstream asset names are retained
only for provenance. They are used as anonymous displacement vectors and are not
claims about the photographed person's demographic identity.

The existing independent target parser maps all six assets to the 4,459-vertex
head. Every direction affects all head vertices. The generated private basis
hash is `f4bba0d100d142f036d586a939018fba3ca58cb876848a107eb07641157332fe`.

## Nonnegative fit

Three deterministic starts fit six nonnegative weights with fixed cameras and a
source prior. The retained candidate moves at most 0.006147 template units,
keeps a 0.953410 minimum triangle-area ratio and has no reversed triangles.

| Diagnostic px | Source | Candidate |
| --- | ---: | ---: |
| Frontal outline A | 4.689129 | 4.779644 |
| Frontal outline B | 7.693239 | 7.607089 |
| Left-oblique outline | 3.150981 | 3.212855 |
| Right-oblique outline | 2.393675 | 2.327741 |
| Left full profile | 3.641965 | 3.557945 |
| Right full profile | 8.032225 | 7.751983 |
| Reviewed anchor mean | 5.226536 | 5.319229 |

Both profiles improve numerically, but one frontal outline, the left oblique and
reviewed anchors regress. Actual five-view inspection shows only a negligible
generic change and no convincing identity or side-profile improvement.

## Centered-difference fit

A same-variable follow-up removes the dominant common direction, computes the
five orthogonal differences among the six assets, normalizes each by maximum
vertex displacement and fits signed coefficients. Every nonzero proposal fails
the unchanged bilateral profile protection; the retained fraction is zero.

Decision: retain the audited CC0 lock as reusable asset evidence, but do not add
this broad macro basis to the reconstruction candidate. It neither supplies the
missing localized eye/nose/lip anatomy nor produces a human-visible improvement.
Continue with a richer local anatomical basis whose effects are directly
constrained by corresponding image regions.

Private reports, meshes and five-view renders remain under `assets/private`.
No photo, biometric coordinate or identity mesh is committed. Existing public
tests and production behavior are unchanged.

