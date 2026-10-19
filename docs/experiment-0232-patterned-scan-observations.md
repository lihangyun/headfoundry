# Experiment0232: fixed nonplanar image truth for observation validation

Date:2026-10-19. Pre-registered before rendering.
Dataset generation:`TECHNICAL_CHECK_PASSED`; real head/camera acceptance:`UNVERIFIED`.

0230/0231 validate rigid3D geometry but not pixel correspondence under image
formation. Create one controlled **local validation dataset**, never training
data or a final head, using the identical supplied case001 scan,5000 material
samples, six cameras, visibility and units from upright0230.

Reuse the existing Blender generator with one explicit non-default appearance
mode. Apply object-coordinate3D Noise Texture (scale48,detail2,roughness0.5),
grayscale ramp0.15->0.75 and emission strength1, Standard view transform.
Emission removes changing illumination as a confound. Export RGBA on a transparent
background. This is a fixed synthetic surface pattern, not photorealistic human
skin or subject texture recovery. No external material/model/download.

Assert bit-identical geometry, camera, point, projection and visibility arrays
against upright0230 before issuing the successful generation report. Source
scan hashes remain unchanged and independent camera replays still pass. Review
all six actual patterned images to verify surface attachment and upright axes.
One180s render run; no texture density, contrast, camera or sampling sweeps.

A subsequent observation experiment must predeclare its independent context/
measurement split, coarse pixel perturbations, interior/visibility population,
unchanged precision/retention gates and failure exit before using these images.
Do not extrapolate a pass to untextured/real skin, occluded pixels, real cameras,
millimeter scan error, complete reconstructed heads or likeness acceptance.
All derivatives stay private/local; case002 and bone scans are not fit or trained.

The7.337713s source-only render run produces six actual patterned views. Every
geometry/camera/visibility array is bit-identical to upright0230; the entire
known-motion NPZ even retains the same SHA-256. Independent camera replay stays
below0.000072px and the source scan hash is unchanged. The frontal image and all
five other views in the later observation sheets were inspected. Patterned
emission intentionally removes anatomical shading; these images are not new
heads or recovered human textures. The original clay generator remains the
default, with an explicit non-default `--patterned` validation mode.
