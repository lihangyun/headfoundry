# 0349: human-specific entry screen after LingBot closeout

2026-10-24. Read-only primary-source screen;no model installation,inference,
patient-data access,training or medical mesh input. Previous0348cleanup352d0e8
is complete. This is source evidence and a new hypothesis,not a quality pass.

## Newly checked candidates

- [UFM publisher README](https://github.com/UniFlowMatch/UFM/blob/main/README.md):
  code BSD3,but released checkpoints explicitly CC-BY-NC-SA4. REJECT integration
  under the project policy. No download. Do not infer weight rights from code.
- [Face Anything official license](https://github.com/kocasariumut/FaceAnything/blob/main/LICENSE):
  CC-BY-NC4. REJECT integration. The official README describes canonical facial
  coordinates and camera/depth outputs;its face-specific formulation is relevant,
  but does not establish permitted use or case001 accuracy. No fork substitution.
- [STFR official README](https://github.com/yxuhan/STFR): masks then COLMAP cameras,
  2DGS geometry and Wrap registration. [Environment](https://github.com/yxuhan/STFR/blob/main/ENV.md)
  explicitly installs Wrap and multiple separately licensed components. Stock
  pipeline not admitted:it neither removes the unresolved camera prerequisite
  nor establishes a fully free commercial dependency chain. GPL code alone is
  not the reason for rejection;no claim GPL forbids commercial use. No install.

## A distinct candidate: DAViD human surface normals

[Microsoft DAViD](https://github.com/microsoft/DAViD) explicitly licenses models
and runtime under MIT;the normal-model card repeats MIT. This is stronger than
an inferred code-only grant. Its synthetic-human training and camera-space
normal output differ from0348generic scene camera regression and0345unknown
lighting fit. This permits further source/asset verification,not deployment.

[Normal model card](https://github.com/microsoft/DAViD/blob/main/model_cards/surface_normal_model.md)
lists Base428.42MB,512square BGRfloat input and3-channel normals. Face benchmark
mean angular error17.33degrees is a serious caution,not a millimetre guarantee.
It explicitly excludes nonhuman object categories and warns against unvalidated
medical use. Therefore the black planar0332fixture is NOT an appropriate model
acceptance test here. No clinical use is proposed. No330GBdataset download.

## Independent calibration hypothesis, not yet implemented

Can perspective normal-field integrability supply focal information without
material point matching? Let x,y be principal-point-centered pixels,f shared
focal length,z depth,and n=(a,b,c) camera-space normal. Orthogonality gives
partial_x log(z)=-a/D,partial_y log(z)=-b/D,D=ax+by+cf.
Equating mixed partials yields B+fA=0,where

    A = c*(partial_x b-partial_y a)+a*partial_y c-b*partial_x c
    B = x*(a*partial_x b-b*partial_x a)
        +y*(a*partial_y b-b*partial_y a)

Thus nonzero A could constrain f;constant normal fields have A=B=0 and cannot.
This derivation assumes a smooth depth graph,known principal point,square pixels,
zero distortion and consistent normal conventions. These assumptions are NOT
verified for case001. Derivative noise and correlated model bias may destroy
the signal. Single-view focal information alone cannot certify multiview poses,
metric scale,2mm surfaces or hidden posterior shape.

Next safe action:one separately preregistered minimal independent numerical
identifiability/conditioning check on original analytic curved surfaces,with
plane degeneracy and exact-geometry controls,BEFORE downloading any model.
No threshold/precision sweep. If that evidence supports a bounded model trial,
first pin official source/model bytes and inspect camera-coordinate conventions;
use an in-domain authorized human/synthetic-human evaluation,not a general-object
proxy. No scan normal targets may enter the reconstruction initializer.

## Status and cleanup

UFM/FaceAnything stock integrations REJECT on rights;STFR stock entry unapproved.
DAViD asset-level permission is supported by primary statements;implementation,
coordinate semantics,calibration utility and physical precision remain UNVERIFIED.
No exclusive runtime,weight,generated output or failed test was installed,so no
binary cleanup is needed. Existing rejected routes stay retired. No new head.
