# Experiment 0167: current-camera held-track transfer

Status: frozen-track evaluation `TECHNICAL_CHECK_PASSED`; current camera and
refined candidate `REJECT` for the 3 px camera gate.

The experiment-0017 LighterGlue report preserves 51 spatially separated
front/left30/right30 matched tracks. Every fifth track (11) was held out
before that camera experiment; its other 40 tracks are the only training
observations. The existing experiment-0132 five-view camera archive was
evaluated on those same 11 tracks without fitting either cameras or geometry.
For each held track, two observed views triangulate a point and the third
view is predicted, cycling all three targets. The 33 correlated predictions
have p95 error **7.373606 px**; all have positive depth. Per-target p95 is
6.541/6.829/6.972 px for front/left30/right30. This is a fresh check on the
*current* camera archive, not the old pairwise initialization. It excludes
both pure profiles and does not prove physical material correspondence.

A single follow-up fit reused experiment 0017's fixed 1800 px intrinsics,
40/11 split, sparse bundle objective, scale gauge, soft-L1 loss and 300-call
budget. Only initialization changed: the experiment-0132 cameras were put in
a front-identity gauge. Training p95 fell from 9.951385 to 3.520518 px, but
the solver reached the 300-call budget without convergence. The untouched
held tracks' p95 was **7.545315 px**, essentially the earlier 7.545592 px
from a different initialization; all held depths remained positive. No
parameter selection or early stop used held errors.

These results reject current-camera acceptance and a claim that a better
starting pose alone fixes the old three-view transfer failure. They do not
identify whether residuals arise from matched-track errors, focal assumptions,
pose, or nonrigid image differences. Repeating this same bundle fit with more
iterations is not justified by the near-identical held result. Next inspect
the high-error tracks against source photos and enforce physical/semantic
correspondence before another camera solve. The local reports, script and
photographs remain ignored under `assets/private/subject-001`; none are
committed or uploaded.
