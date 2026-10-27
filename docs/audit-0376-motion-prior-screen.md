# 0376 motion-prior admission screen

2026-10-28,after failed0375cleanup9bae3fd. Read-only evidence review; no model,
camera fit,scan fit,training,dependency installation or production change.

## Question

Could a fixed head-rotation center supply the missing independent camera
information instead of another learned depth source? Reinspected original
case001 intake contact sheet,0252coverage,0257material audit,0255unknown-pose
silhouette experiment,0329joint-view information and0345light audit.
The old intake frame labels include known seek offsets documented in0252;
this thumbnail review supplies neither new frame identities nor measured angles.

## Evidence and decision

- Video visibly contains yaw and pitch phases with neck changes. This does not
  establish a single fixed physical axis,center or constant angular increments.
  It also does not quantify how much center drift exists. Do not assume either
  exact turntable motion or that all such models are impossible.
- Oxford's author publication page for Fitzgibbon/Cross/Zisserman1998 describes
  single-axis reconstruction with unknown/nonconstant angles but a remaining
  two-parameter ambiguity; extra scene/camera information is needed to remove it.
  Source:https://www.robots.ox.ac.uk/~vgg/publications/1998/Fitzgibbon98a/
  This is a scope check of the abstract,not a complete algorithm reproduction.
- The2006Cao/Xiao/Foroosh/Shah turntable method's author-hosted abstract assumes
  constant inter-frame rotation when allowing zoom/focus variation. Full PDF
  retrieval timed out; do not claim full-paper verification or implementation
  readiness from the abstract. No measured constant-angle sequence is available.
  Source:https://stars.library.ucf.edu/facultybib2000/4660/
- Crucially,fixed-pivot motion is NOT an unexplored project idea:0255already
  used common translation/unit-radius rotational-object cameras and failed all
  independent projection gates. Simply imposing a pivot again or restricting
  its degrees of freedom is not a new justified route and is not admitted.
- 0329shows common points across an independent third-axis view can add local
  focal information in an owned fixture. It also shows observation-wise holdout
  destroyed that information. Whole-point holdout and the verified0332backend
  therefore remain useful; no new synthetic rank experiment is needed.
- 0333failed before that backend because no complete cross-axis correspondences
  were admitted. A motion prior alone does not supply missing physical identities.

Decision:do not launch a turntable/pivot solver or revive silhouettes. Current
missing prerequisite is independently supported common-point observations
across differing motion directions,not lack of another free-pose optimizer.
Any next candidate must state how it obtains that information and handles
occlusion/nonrigidity without declaring semantic labels,cycle closure or low
training residual to be ground truth. Actual3px/2mm/head acceptance stays
UNVERIFIED. This screen eliminates a tempting duplicate experiment; it is not
an improvement to the reconstructed head or a newly selected implementation.
