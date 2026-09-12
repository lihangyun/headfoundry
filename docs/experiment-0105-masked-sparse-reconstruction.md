# Experiment 0105: affine SIFT sparse reconstruction feasibility

Status: `REJECT` for five-view reconstruction. Both actual runs finish without
a sparse model; no new head or accepted camera is produced.

## Question and fixed conditions

Before attempting dense stereo, test whether image features can recover a
connected five-view reconstruction of the authorized subject. Reuse the five
original images and the early experiment's ellipse masks, without modifying
existing cameras or meshes. The masks restrict keypoint centers to head regions;
they are not accurate skin segmentation, and some hair/background remains.

The primary variable is standard SIFT versus affine-shape, domain-size-pooled
SIFT. Both use the same local PyCOLMAP 4.2.0 CPU runtime, 1254 px maximum image
size, peak threshold 0.003, four workers, exhaustive matching and default match
thresholds. The single shared SIMPLE_RADIAL camera starts at the default focal
factor 1.2 (1504.8 px). This remains an uncalibrated assumption. RANSAC and mapper
seeds are 17; mapping has a 120-second budget. COLMAP's built-in initialization
relaxations remain enabled and are not HeadFoundry acceptance thresholds.

## Recovered historical evidence

The original database contains 17,370 keypoints; all lie inside the intended
nonzero masks when sampled with floor pixel coordinates. Its five feature
counts are reproduced exactly by this run. The old mask filenames omit the
extra `.png`, but the [4.2.0 reader implementation](https://github.com/colmap/colmap/blob/4.2.0/src/colmap/controllers/image_reader.cc)
explicitly supports extension replacement as a fallback. The historical failure
must not be explained as masks being silently ignored.

## Actual results

| View | Standard keypoints | Affine / pooled keypoints |
| --- | ---: | ---: |
| Front | 4529 | 4834 |
| Left oblique | 4239 | 4511 |
| Left profile | 2190 | 2357 |
| Right oblique | 4230 | 4543 |
| Right profile | 2182 | 2396 |

Every extracted keypoint center is within its mask in both runs. Standard SIFT
produces no verified pair. Affine/pooled SIFT produces one verified front/right
oblique pair with 26 inliers, representing 25 distinct rounded pixel locations
in each image. The other nine pairs have zero verified support, including all
profile connections. Mapping rejects its initial pair and returns no model.

The private pair overlay was inspected: much of the support lies near eyes and
brows, with sparse mouth/skin/hair support and some questionable matches. It
does not establish physical correspondence or usable nose/lip/chin coverage.
Neither a pair inlier count nor its training error would substitute for the
existing frozen held-out camera gate. No new held-out camera result exists.

Baseline report SHA-256:
`dffe581830cc4357cfa3963d10c6ad7795ab6d9fcb807bdfadf275e0072957d9`.
Candidate report SHA-256:
`59b928c4efddb619bb793654525d0c7bccb6658e6bb06646986e95a7d4e18b5e`.
All databases, masks, input hashes and visual evidence remain local/private.

## Runnable implementation

`tools/run_masked_sfm.py` checks consent and input hashes before importing
COLMAP, validates decoded image/mask dimensions and mask coverage, rejects an
existing output directory, and records exact settings and intermediate/final
results. Missing masks cannot become an unmasked run. It accepts both verified
upstream mask spellings, copies selected masks with the documented appended
extension, then verifies actual extracted keypoint centers against them.

`examples/pycolmap-runtime-lock.json` pins the existing Windows CPython 3.12
extension and COLMAP license bytes. It is a local experiment lock, not a complete
redistribution audit of bundled native dependencies. No binary is committed.
The source package states BSD-3-Clause and separately licensed dependencies in
[COPYING.txt](https://github.com/colmap/colmap/blob/4.2.0/COPYING.txt).

```powershell
$env:PYTHONPATH = 'C:\workspace\headfoundry\src'
.venv/Scripts/python.exe tools/run_masked_sfm.py <manifest> <masks> <new-standard-output>
.venv/Scripts/python.exe tools/run_masked_sfm.py <manifest> <masks> <new-affine-output> --affine
```

The CLI exits nonzero for `REJECT`. Tests cover missing rights before runtime
loading, runtime drift, mask spelling/missing/dimensions/empty coverage, and
non-overwrite behavior using synthetic files. PyCOLMAP remains optional and is
not installed as a base package dependency.

## Decision

Do not begin COLMAP dense stereo from these failed sparse results or relax the
camera gate to accept a disconnected pair. This experiment does not prove that
the photographs are unusable or that all multiview methods fail.

The next independent candidate is the explicitly Apache-2.0
`facebook/map-anything-apache`, which predicts dense geometry as well as cameras.
Its exact model variant, source, offline loading and real execution must be
verified before evaluating cross-view surface agreement. Its noncommercial
default variant is not an alternative. No measured quality gain is implied by
the model's availability.
