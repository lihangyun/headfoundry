# Experiment 0168: inspect the frozen camera tracks as material evidence

Status: original-photo crop audit `TECHNICAL_CHECK_PASSED`; track set
`REJECT` as a sufficient whole-face camera-acceptance population. The
experiment-0167 numerical camera rejection remains unchanged.

All 11 experiment-0017 held tracks were cropped at their saved front,
left30 and right30 coordinates in the five-photo local consent scope. The
cropped sheet and script remain ignored local files, never uploaded. The
three highest individual third-view residuals from the current camera are:

| Track / target | Error | Original-photo region |
| --- | ---: | --- |
| 30 / left30 | 7.59 px | dense eyebrow hairs |
| 50 / right30 | 7.56 px | eyebrow tail / weak hair texture |
| 40 / front | 7.25 px | smooth brow-to-nose skin without a unique point |

The crop review shows that these locations do not have a reliably identifiable
single physical pixel shared by all three photos. This is a correspondence
*risk*, not proof that the matcher chose a wrong point or that the camera is
correct. Other held tracks are concentrated at eyelids, canthi and a lip
point. None directly validates pure-profile pose, nasal tip, chin or rear
head. The 33 numerical predictions are correlated observations of only 11
tracks, and their spatial concentration matters.

Consequently, keep the current camera gate failed: 7.374 px p95 exceeds its
3 px threshold. Do not delete hard tracks, recompute the metric on an
after-the-fact easy subset, or call this a passed camera. Equally, do not use
that number alone to justify a camera-only correction. The next camera
experiment needs a *predeclared* independently reviewed set of stable,
spatially distributed material landmarks, including nose, mouth and jaw,
plus untouched profile evidence and existing physical camera checks. This
audit did not fit or promote any camera, mesh or hairstyle.
