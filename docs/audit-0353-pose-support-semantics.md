# 0353: audit the meaning of the 0352 seed rejection

2026-10-25, read-only scientific audit after cleanup860c2e4. No patient
observation replay, no threshold modification and no model restoration.

The exact archived initializer names the recoverPose return value `positive`
and rejects below90% of the Essential inlier count. The name does not establish
that all excluded points have negative depth. Official OpenCV4.x source uses
both positive depth and a maximum depth filter in both cameras, intersects with
the supplied mask and returns the best of four candidate support counts. Its
no-distance-argument overload supplies50 in unit-translation coordinates.
Source inspected2026-10-25:
https://github.com/opencv/opencv/blob/4.x/modules/calib3d/src/five-point.cpp
This moving4.x source is explanatory, not asserted identical to installed5.0.

Local version verification uses two original exact16-point scenes at depths
20..21.5 and100..101.5, translation[1,0,0], known essential matrix and focal1200.
All32 constructed points have positive depth in both cameras. Test the ordinary
overload without varying any API threshold. This generic API-contract regression
does not claim physical reconstruction progress or reopen0352.

Implication:0352 should be described as recoverPose seed-support REJECT, not a
demonstrated pure cheirality defect. Since E, candidate matrices and per-point
support reasons were not saved before the exception, the clinical cause cannot
be determined from its retained receipts. Far-depth rejection is a possibility,
NOT the verified cause, and increasing the threshold would be an unauthorized
rescue sweep. No revised pass, camera, metric accuracy or head is inferred.
Any future independently justified solver must report raw depth, distance-based
filtering, masks and candidate ambiguity separately before rejecting; preserve
the actual3px/2mm gates. Existing production and successful fixture solvers stay
unchanged in this audit.

Actual local check: cv2 runtime5.0.0, known-positive counts[16,16], API returned
[16,0]; one test passed in0.002s. Confirms the non-equivalence on this installation,
not the exact clinical rejection reason. Test remains as a generic regression.
Full remaining suite164 tests passed in8.735s. No production solver changes.
