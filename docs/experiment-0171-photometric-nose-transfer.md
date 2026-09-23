# Experiment 0171: local photometric transfer and bounded nose-depth test

Status: fixed-camera photo-association check `TECHNICAL_CHECK_PASSED`;
one-mode nose candidate `REJECT`, visible identity quality `UNVERIFIED`.

This uses only the five locally consented photos (the tested train/hold-out
subset is front, left30 and right30), unchanged experiment-0132 cameras and
head, and existing NumPy/OpenCV rasterization. No external image or biometric
data was uploaded. A CUDA differentiable renderer was not installed:
[nvdiffrast's upstream license](https://github.com/NVlabs/nvdiffrast/blob/main/LICENSE.txt)
limits non-NVIDIA use to non-commercial research/evaluation, so it does not
meet HeadFoundry's commercial-rights rule. PyTorch itself is permissively
licensed, but installing another runtime would not resolve this geometry
question.

As a feasibility control, 971 vertices visible from all three views were
sampled in blurred Lab color under the same mesh/cameras. Their median
same-surface three-pair color gap was 14.625 OpenCV Lab units, versus 29.730
after deterministic cross-view shuffling. Moving the two oblique photo
sampling positions only five pixels diagonally raised it to 20.330. This
shows some image-position-sensitive cross-view association, not verified
material correspondence or a quality metric.

The predeclared candidate changed only one smooth nose-depth field by a
coefficient on a 21-value grid from -0.03 to +0.03 model units. The fixed
front/left30 color gap selected -0.009 from 458 common-visible nose samples:

| Gap, median OpenCV Lab units | Baseline | Selected |
| --- | ---: | ---: |
| Front/left30, used for selection | 7.300 | 7.276 |
| Front/right30, held from selection | 10.222 | 10.508 |
| Left30/right30, held from selection | 13.077 | 13.098 |

Maximum displacement is 0.00899 units, minimum relative triangle area is
0.9549, and no face normal reverses. The tiny fitting gain fails to transfer
to the untouched right-oblique photo; the candidate is `REJECT` without
spending a full five-view render on an unpromotable millimetric change. Fixed
baseline visibility and color centering also limit interpretation. Do not
claim that photometric consistency has solved camera or identity. Any later
dense-image route needs richer coherent shape freedom and independent visual
and profile checks; repeating this one-mode sweep is not justified.

The local candidate OBJ, reports and original photos remain ignored under
`assets/private/subject-001`. No formal texture implementation or baseline
replacement was made while the camera gate remains failed.
