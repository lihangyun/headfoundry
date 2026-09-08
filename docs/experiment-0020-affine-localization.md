# Experiment 0020: bidirectional local affine alignment

Date: 2026-09-08. Candidate not adopted. Camera and final reconstruction remain
unaccepted; no old observation, baseline, or acceptance threshold changed.

The hypothesis was that local foreshortening explains the translation tracker's
failure. All 51 original tracks were tested without camera predictions or
camera-error selection. Each frontal/intermediate pair uses original grayscale
61x61 subpixel-centered patches and six-parameter ECC affine alignment in both
directions. Settings were fixed before execution: 100 iterations, epsilon 1e-5,
Gaussian size 5, minimum correlation 0.85 in both directions, at most 6 px center
shift, at most 1 px composed forward/backward center discrepancy, positive
determinants and singular values between 0.5 and 2 for both affine transforms.

A deterministic synthetic affine image test recovers the known center mapping
to 0.00523 px, with correlation 0.95315. This confirms the local mapping direction
and bounded algorithm invocation, not performance on facial photography.

Of 102 real pair checks, 97 return transforms in both directions. Of those, 63
meet the correlation requirement, 58 the shift bound, and 12 the roundtrip bound.
These are overlapping counts, not independent categories. Nine pair checks pass
all constraints; zero complete three-view tracks pass both pairs. Consequently
there is no accepted training/held-out replacement set and no camera refit.
Every original/candidate location and rejection is retained in private output.

This refutes the sufficiency of this bounded local affine method for the current
matches. It does not prove that no physical correspondences exist, that the
photographs are invalid, or that the current cameras are accurate. In particular,
high patch correlation is not enough to claim repeatable point localization.
The earlier description of some points as unreliable is an uncertainty finding,
not a verified causal diagnosis of the camera failure.

The remaining practical requirement is a set of independently verifiable rigid
surface anchors with adequate spatial coverage. Neither additional initialization
model swaps nor another acceptance threshold relaxation is supported by the
current evidence. Formal head and texture implementation remains behind the
unchanged camera gate; no KeenTools or MV-HRN quality comparison is claimed.
