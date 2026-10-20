# Audit0260: bounded replacement-route eligibility screen

Date:2026-10-20. Registered before adoption/install or a new reconstruction run.
Previous0259 is completed progress and retired at16ef4c8,not a live job.
Full goal remains unmet;do not replace it with a successful technical subtask.

Screen at most four distinct candidates from primary official sources only:
Fast3R,Pow3R,D4RT and GeoCalib. First search identifies the former three;it does
not establish eligibility or authorize downloading code/weights. GeoCalib is a
different intrinsic/gravity cue,not a pointmap/shape replacement. Repository
history search has no Fast3R/Pow3R match;this does not clear their licenses.

Question:does any candidate supply a freely commercially permitted,available
and materially different camera/observation mechanism with a defensible local
test path,without restoring a rejected integration or feeding patient scan into
video inference? Require explicit code and checkpoint rights,actual released
artifact availability,what camera quantities are recovered,and untested
assumptions/compute dependencies. Paper concepts,third-party miniature replicas
and an open code license alone do not satisfy checkpoint/model readiness.

Budget:15minutes wall time from this registration,at most four candidates,no
weights/framework/environment downloads,no training,private uploads or extra
fit/model trials. Read-only official source/metadata requests are allowed.
Record primary links,precise conditional eligibility and why a model could or
could not address independent head-camera/material evidence. Do not manufacture
a fifth candidate or claim exhaustive proof that no open-source solution exists.
If none justifies implementation,record the missing prerequisite instead of
another arbitrary model swap or revival of0251/0256/0259 numerical variants.
No camera/geometry/visual acceptance or successful training follows this audit.

## Completed screen: two excluded,two conditional information paths

Screen completed in733.737s of the900s wall budget,including the interruption;
the timer was not reset. Four candidate families only,no model/framework
downloads,environment installation,inference,human input read or training.

| Candidate | Published rights / release evidence | Decision for this goal |
| --- | --- | --- |
| Fast3R | Official FAIR Noncommercial Research License covers code,weights and related materials. | REJECT adoption under our commercial-use rule;no accuracy trial. |
| Pow3R | Official license explicitly restricts the materials,including checkpoints,to non-commercial purposes. | REJECT adoption;do not request a paid license or silently reuse weights. |
| D4RT family | Original authors' project/blog describe native3D temporal/camera queries,but inspected official pages do not establish a deployable licensed checkpoint. A distinct unofficial OpenD4RT release does exist. | Original release availability UNVERIFIED;OpenD4RT is a provisional research lead,not a validated substitute or endorsement by Google. |
| GeoCalib | Code Apache-2.0;explicit model-weight grant CC-BY-4.0. Released pinhole/distorted weights and CPU-capable interface exist. | Rights/availability support an optional calibration component,not a complete head-pose/material route. Local accuracy/runtime/dependency review UNVERIFIED. |

Primary evidence,checked2026-10-20:

- [Fast3R license,33104d4b5b8df43795ecded236194958bbdac572](https://github.com/facebookresearch/fast3r/blob/33104d4b5b8df43795ecded236194958bbdac572/LICENSE).
- [Pow3R license,25d7bb68e01336585b5277d5d6aafadddf9e1b8d](https://github.com/naver/pow3r/blob/25d7bb68e01336585b5277d5d6aafadddf9e1b8d/LICENSE).
- [D4RT original project](https://d4rt-paper.github.io/),[Google DeepMind explanation](https://deepmind.google/blog/d4rt-teaching-ai-to-see-the-world-in-four-dimensions/).
- [GeoCalib rights,1dedb29f94fc11b896c5f572005978aeebccd67f](https://github.com/cvg/GeoCalib/blob/1dedb29f94fc11b896c5f572005978aeebccd67f/README.md#license),[weight license](https://github.com/cvg/GeoCalib/blob/1dedb29f94fc11b896c5f572005978aeebccd67f/LICENSE-WEIGHTS),[model interface](https://github.com/cvg/GeoCalib/blob/1dedb29f94fc11b896c5f572005978aeebccd67f/geocalib/extractor.py).

### GeoCalib cannot supply the missing complete head-relative camera

Its outputs are camera intrinsics and gravity;principal point is assumed centered.
Shared intrinsics do not infer unknown relative rotations of a moving head,and
the rigid-rig interface explicitly requires known rig rotations. Do not rename
focal/gravity predictions as a full object-to-camera SE3 or physical tracks.
Published dataset AUC is not evidence for ourcase0013px gate. Released assets
are116074121bytes (pinhole) and116143955bytes (distorted);no local speed/memory
measurement or checkpoint hash/complete import clearance is asserted here.

A new pure-NumPy shared camera regression supplies a counterexample:two proper,
positive-depth cameras share exact K and gravity,but a15deg yaw plus translation
changes the8 fixed nonplanar-point projections by66.896px p95. This proves
these outputs alone leave pose ambiguous;it does not prove image-based pose
recovery impossible. No patient shape or geometry fitting is used by the check.

### OpenD4RT is available,but not yet cleared or runnable here

[Authors' independent implementation](https://github.com/Lijiaxin0111/Open-d4rt/tree/403290a6e7ea6262a1f20f8c02d5461cd7b6c9b3)
explicitly calls itself unofficial. Its own code is Apache-2.0 and its
[published model repository](https://huggingface.co/Lijiaxin0111/OpenD4RT/tree/7099b1fc760475de3b7409acd6b63f801b015d07)
declares Apache-2.0 and is ungated. It is not one of the untrained tiny replicas
seen in search results,and must not be confused with the original D4RT release.
Two actual checkpoint objects exist:32-frame13950006682bytes and48-frame
13950737434bytes (about13.95decimalGB each). Official repository metadata gives
LFS SHA2561f63305422fdc2000b057fbbc1d37459ac1a8063bbfcd0e3b7d473f5485943f5
and65936f72eb902f9a3629e25b2888e8cc2ebf87a89bee7103fe94313fb53dd179.
These are published identities,not downloaded-byte verification.

This independent3D coordinate-query mechanism is a materially different lead
from0259's recurrent2D pixel tracker. However upstream pretrained initialization,
checkpoint rights/provenance,executed imports,hardware/peak-memory feasibility
and actual known3D camera/point accuracy remain UNVERIFIED. Code/license badges
and authors' WorldTrack numbers cannot clear all those gates. No14GB download,
model switch,private-data demo or claimed head improvement is justified yet.

## Decision and next permissible gate

Do not install an NC alternative or treat GeoCalib as an SE3 initializer. The
next defensible action is a separately bounded **OpenD4RT provenance and local
resource preflight using public metadata/source only**,before any download or
patient inference. If it cannot be cleared or cannot fit a credible resource
budget,stop that lead instead of training a tiny unrelated replica,changing
precision or reviving earlier integrations. This is not an exhaustive proof
that no open-source solution exists and does not require user action yet.

Source URLs/commits/document hashes/release metadata and budget are recorded
locally in `assets/private/replacement-route-screen-0260/source-evidence.json`.
No failed integration was created,so there is no model/runtime cleanup to
perform. Full objective,camera/material gates and actual visual acceptance
remain unmet and unchanged. Production source/defaults,original materials,
success fixtures and unrelated0207 draft remain untouched.

Final133 shared tests pass in4.846s,including the new independent camera
ambiguity regression. This is a safety/claim-boundary check,not a head-quality
improvement. No failed integration or disposable binary is created by the audit.
