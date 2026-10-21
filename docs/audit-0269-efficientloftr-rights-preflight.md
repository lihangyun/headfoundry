# Audit0269: exact EfficientLoFTR release, not a blanket license badge

Date:2026-10-21. Public text/metadata/source inspection only; no weight download,
new environment, model execution, human input, training or upload in this audit.

The proposed information change is direct detector-free, pair-conditioned
matching across the real0267 component gap, rather than extending retired DIS
tracks or replacing missing identities with labels. Published scene results do
not establish skin correspondence, head-relative rigidity or camera accuracy.

## Rights identities and the apparent conflict

- Current author source commit `07e9c1401e71e9c556b1fda9d86d060af36ba176`
  adopted [PRL1.0](https://github.com/zju3dv/EfficientLoFTR/blob/07e9c1401e71e9c556b1fda9d86d060af36ba176/LICENSE)
  on2026-09-15. Its organizational project use requires prior registration,
  including contact/entity/project information, even for development/testing.
  Registration is described as free and automatic, not paid or approval-gated.
  We do not submit this form, assume a personal exemption, or adopt this source.
- The author's immediately preceding source
  `ffd4a4644064354468eb1f0c7a3e732233cb732f` has the older
  [Apache2 license](https://github.com/zju3dv/EfficientLoFTR/blob/ffd4a4644064354468eb1f0c7a3e732233cb732f/LICENSE).
  Its [README](https://github.com/zju3dv/EfficientLoFTR/blob/ffd4a4644064354468eb1f0c7a3e732233cb732f/README.md)
  explicitly endorses the Transformers integration and links the exactHF model.
- The independently published, ungated
  [zju-community/efficientloftr model](https://huggingface.co/zju-community/efficientloftr/blob/face1a79050ffa3e9da28720d1cf93aaf2e8f421/README.md)
  revision `face1a79050ffa3e9da28720d1cf93aaf2e8f421` explicitly declares Apache2.
  Metadata dates this revision to2025-08-18, before the2026 source-license switch.
  Thus do not apply today's PRL source label to every historical/code/model asset,
  or assume an unrelated model card overrides the current native source terms.
- The proposed runtime is only Apache2 Transformers4.57.1, commit
  `8cb5963cc22174954e7dca2c0a3320b7dc2f4edc` (2025-10-14), whose model,
  processor and configuration files have explicit Apache headers. No current
  native ZJU implementation, GoogleDrive pickle, sample photographs, training
  corpus or externally initialized backbone is needed on this reviewed path.

These independent pinned grants support a bounded local trial of that historical
HF release and HF implementation, not the current PRL source. This is reliance
on published rights/provenance, not a legal opinion about every training contract,
patent, output or redistribution. Preserve notices; fail closed on identity or
license changes. No project-registration action or new user disclosure is needed
for this selected path. Actual checkpoint bytes are still UNVERIFIED here.

## Concrete engineering findings

Expected safetensors:64263488bytes, LFS SHA256
`00a5edc343fa222eba763643553548ad37a05aa3d00d266553c9f6cf67bb0e64`,
metadata16050816FP32 parameters. This is not measured peak RAM or throughput.
Config SHA256`eaa141ed38f64ec65efe7b663338e2b44d260ff2b26f5829624e5241ff29f1d8`;
processor SHA256`22151d20a71d5d25bee2b5f5c3a5999befa3285597218a9d1ea63998f84dc606`.

The model uses ordinary Torch operators with no hard CUDA call on its inspected
forward path. CPU execution still needs testing. Its public480x640 processor
distorts aspect ratio by default; any experiment must explicitly preregister its
own fixed pixel transform and inverse, not hide this in camera estimates.
The HF visualization postprocessor **casts coordinates to int32**. Preserve the
forward model's normalized floating coordinates and explicitly invert scaling;
do not turn an integer display helper into a subpixel measurement pipeline.

No fresh model/3D capability or actual camera/head has passed. Rights/source-path
screen is TECHNICAL_CHECK_PASSED in that limited scope; execution, correspondence,
rigidity,3px cameras,2mm surface and actual whole-head acceptance are UNVERIFIED.
Next is one separately preregistered small pixel/candidate-readiness test, not
head fitting. Small public source snapshots/hashes stay local under
`assets/private/efficientloftr-preflight-0269`; no failed binary integration exists
to clean. Defaults, shared runtime, original human data and unrelated0207 stay
unchanged. Do not automatically install the PRL/native or another checkpoint.
