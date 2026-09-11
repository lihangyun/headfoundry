# Experiment 0084: protect each profile row during joint fitting

Status: `REJECT` as an improvement; retained geometry is unchanged.

Single change from experiment 0083: add a penalty of 100 times any increase
in absolute error at every original row of both profile curves. Keep the same
ten signed CC0 controls, fixed cameras, source, point observations and three
starts. After solving, enforce each row's source error plus a 1e-6 px numerical
tolerance with step fractions 1, 1/2, 1/4, 1/8, 1/16, 1/32 and zero.

The zero start converges in 23 evaluations at penalized cost 44.551898.
The +0.1 and -0.1 starts both reach the 120-evaluation limit and are excluded
from candidate selection, despite finite costs 45.687456 and 44.556613.
No claim is made that all branches or constrained optima were explored.

Every tested nonzero step from the converged solution violates at least one
profile-row guard. The retained step is zero: all ten weights and maximum
movement are exactly zero before serialization. Both local profile MAEs remain
3.716699/8.033169 px and all three point means remain 6.840646/9.750968/7.474708.
The exported OBJ was independently reopened: faces match exactly and maximum
coordinate difference from the source is 4.99974e-9 template units, consistent
with the existing writer's decimal rounding. No new visual improvement exists;
rerendering an unchanged model would add no evidence.

This is a limitation of this penalty-plus-step-search procedure on these
observations, not proof of infeasibility for the whole shape space. In
particular, per-row protection is deliberately stricter than aggregate error
and can reject changes that redistribute annotation noise. The technical
runner reports UNVERIFIED because its triangle/visibility checks pass; the
experiment rejects the result as progress in likeness.

Decision: do not repeat this penalty or loosen profile protection merely to
claim an improvement. Resolve mouth-surface correspondence semantics and
annotation uncertainty before stronger joint fitting. No candidate promotion,
camera acceptance or identity claim. The private runner and
`joint-nasolabial-protected-v1` retain the solve and report; public production
code remains unchanged. Checks were the actual three-start solve, per-row
step guard and independent OBJ reopening. No personal data is committed.
