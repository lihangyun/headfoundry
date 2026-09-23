# Experiment 0174: fixed-geometry Gaussian appearance transfer

Status: local renderer/back-propagation `TECHNICAL_CHECK_PASSED`; appearance
on fitted views `PARTIAL_SUCCESS`; cross-view visual transfer and use as a
reconstructed head `REJECT`.

This private diagnostic used the unchanged experiment-0132 cameras, 10,000
sampled points from the current head and 10,000 from the previously rejected
hair visual hull. Point positions and rotations were frozen; only RGB, opacity
and scale were optimized for 300 steps at 256 px with gsplat 1.5.3. Four
photos (front, left30, left90, right30) supplied color losses. The right90
photo supplied no color loss, but **did** inform the pre-existing hair-hull
geometry. It is therefore excluded only from appearance fitting, not a fully
independent reconstruction holdout. The five photos, sampled points, local
script, images and numerical report remain ignored private data.

Masked RGB L1 on the fitted front/left30/left90/right30 views fell from
0.244/0.206/0.139/0.221 to 0.051/0.049/0.039/0.029. Right90 changed only
0.1534 to 0.1528. The actual front and left-profile renders become more
recognizable, but retain conspicuous speckles, incomplete eyes/neck and the
rejected block-like bun. The right-profile render retains extensive skin and
hair blotches; it is not a credible portrait of the photographed subject.
Lower fitted-view error is not evidence of a consistent appearance field or
subject likeness. No mesh is produced, the seed geometry was already rejected,
the cameras remain unaccepted, and no formal texture/default is promoted.

The next falsifiable experiment should resolve the surface/occlusion problem
before more appearance steps: use a single coherent 3D surface, assign color
only from source-visible skin/hair evidence, and compare both pure-profile
renders with the photos under the same camera and crop. Withhold the tested
profile from *both* geometry and appearance creation for an independent
transfer check. More training on the current point cloud is not justified.
