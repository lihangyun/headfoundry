# Experiment 0156: bounded synthetic identity generator

Status: deterministic generation and mesh safety `TECHNICAL_CHECK_PASSED`;
identity diversity and subject quality `UNVERIFIED`.

The generator converts the 348-target lock into 82 bilateral, paired neutral
controls. It combines `decr/incr`, `down/up` and `backward/forward` targets,
joins matching left/right controls, and excludes unpaired assets, explicit
mouth/jaw expression tokens and the separate asymmetric folder. Each identity
activates at most 12 controls with a fixed seed and bounded magnitude.

`headfoundry.synthetic_identity` is deterministic and rejects a sample unless
maximum displacement, minimum relative triangle area and relative normal
orientation all pass. The first real run creates 256 identities on the common
4,459-vertex topology. Maximum displacement is 0.1914, minimum area ratio is
0.4117, no triangle reverses and the worst sample needs two attempts. A fixed
12-sample front/profile contact sheet shows coherent, unbroken heads without
an obvious expression leak or catastrophic artifact; visible diversity is
present but still modest.

Generation and geometric safety are `TECHNICAL_CHECK_PASSED`. The contact
sheet is a plausibility screen, not demographic coverage, anatomical truth or
subject reconstruction evidence. Diversity, realism and KeenTools-level
quality remain `UNVERIFIED`; no real photograph is included in the generated
set.

Next gate: fit the 82-control piecewise nonlinear manifold directly to the
five local subject views under the existing camera, bilateral held-profile,
oblique, eye and mesh protections. This is preferable to training a neural
decoder before proving that the source manifold can represent the subject. A
candidate must visibly beat experiment 0132 in exact Blender overlays.
