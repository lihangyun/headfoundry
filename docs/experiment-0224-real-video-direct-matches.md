# Experiment0224: direct descriptor observations on the real development video

Date:2026-10-19. Pre-registered before extraction.
Observation preflight:`TECHNICAL_CHECK_PASSED`; camera acceptance:`REJECT` in0225.

## Hypothesis and protected controls

0222 rejects frozen-cloud held localization and pixel rigidity;0223 cannot
retain enough independently cycle-consistent LK supports. Stop that family.
Test the existing locked Apache-2.0 XFeat extractor plus LighterGlue matcher on
the actual real video. Unlike transported LK identities, each frame's features
are independently detected and associated by descriptors/context. This is a new
observation mechanism, not a flow/focal threshold sweep. Its old results on
independently generated AI images do not predict this real-video result.

Reuse exactly0219's52 saved frame PNGs, conservative face masks, same249 saved local
pair list, original shared SIMPLE_PINHOLE camera prior1500/360/640,2px geometric
verification and3px mapping filters. Top4096 whole-image XFeat detections are
then filtered with the unchanged mask before matching, using the existing
strictly loaded LighterGlue configuration and confidence0.1. No data training,
downloads, fallback model, scan geometry, held624/1040, case002 or changed masks.
Validate exact asset/runtime/license/input hashes before loading local weights.

Save observations/matches and require >=50 geometrically verified supports on
>=80% adjacent frame pairs, >=80% frames in one verified connected component,
and both original profile intervals in that component. Save the maximum
non-homographic-support initial pair using0221's unchanged deterministic rule
(>=50 verified,H support<0.8), and inspect its actual supports before mapping.
Failure stops without camera or head fitting. No extra pairs or threshold sweep.

If observation preflight and support review pass, one mapping attempt may use
that selected pair and otherwise exactly the established mapping parameters.
All0221 preliminary gates still apply, followed by independent observation and
reserved-frame checks. Mapping success alone remains `UNVERIFIED`.

Budget:600s for observations/verification,300s for at most one map. Keep first
outputs/errors; ordinary API/implementation repairs are separate report-only or
exact-observation replays, never hidden parameter changes. This diagnostic uses
only existing free-commercial assets and CPU inference, not model training.

## Actual results

Strict loading verifies the already pinned extractor, matcher and runtime;
all6 original private asset hashes/rights are checked. The52-frame extraction,
249-pair association and verification finish in29.850493s. Selected features
range93-487 per image;48/51 chronological adjacent pairs have>=50 verified
supports, and one component contains all52 frames and both profile intervals.
The deterministic initializer selects image IDs3/4 (frames24/36),245 verified
matches, homography support0.346938776, score160. Actual selected photo supports
were inspected before mapping: ear/cheek/nose/eyelid/mouth, not blue background.
This does not certify every point's physical correspondence.

One report-ordering bug is repaired without repeating extraction/matching:
database image IDs9/10 correspond to nominal108/96, not chronological order.
The original producer is retained as an exact hash-matching source capsule.
`chronology-audit.json` recomputes adjacency from actual frame names, and still
passes48/51; old report/database/selection are unchanged. A unit test explicitly
covers swapped database IDs and unordered ID-pair keys. Future reports use
chronological frame order directly.

One12.326089s mapping attempt registers52/52 frames,1639 points,11408
observations, mean track length6.96034 and focal1083.257882px. Training p95 is
2.618121px and all preliminary gates pass. Independent binary-model versus NPZ
replay for all points, camera extrinsics and intrinsics has maximum error0.
Actual three-view sparse projections and all-point clouds were inspected; no
point trimming or surface completion was performed. The output has0 faces and
is not a complete/editable reconstructed head.

0225's subsequent direct-match localization rejects both development sentinels.
Thus the candidate is not promoted despite broad training registration. It is
not legitimate to compare its2.62px training residual to0221's2.26px or0225's
7.83px held-pixel residual as a common-population likeness improvement.
No weights are trained/downloaded and no source scan geometry enters this run.
