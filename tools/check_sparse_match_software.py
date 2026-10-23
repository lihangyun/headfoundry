"""Owned CPU operator/index controls; no weights, images, or model inference."""


def check(torch, aliked_module, matcher_module):
    def require(condition, message):
        if not condition:
            raise AssertionError(message)

    def exact(actual, expected, message):
        require(actual.device.type == 'cpu' and actual.dtype == expected.dtype,
                'CPU/dtype contract: '+message)
        require(torch.equal(actual, expected), message)

    def floats(values):
        return torch.tensor(values, dtype=torch.float32, device='cpu')

    # Dyadic coordinates make these float32 operations exact, not pixel tolerances.
    normalized = []
    cases = (
        ([128, 96], [[0, 0], [64, 48], [127, 95], [16.25, 32.5]],
         [[-1, -.75], [0, 0], [63/64, 47/64], [-47.75/64, -15.5/64]]),
        ([720, 1280], [[40, 320], [360, 640], [680, 960], [200, 800]],
         [[-.5, -.5], [0, 0], [.5, .5], [-.25, .25]]),
    )
    for size, points, truth in cases:
        xy = floats([points])
        actual = matcher_module.normalize_keypoints(xy, floats([size]))
        exact(actual, floats([truth]), 'explicit W,H normalization')
        exact(actual*(max(size)/2)+floats(size)/2, xy, 'pixel roundtrip')
        wrong = matcher_module.normalize_keypoints(xy, floats([size[::-1]]))
        require(not torch.equal(wrong, actual), 'swapped W,H negative witness')
        normalized.append({'size_wh': size, 'points': len(points),
                           'exact_normalization': True, 'roundtrip_max_abs_px': 0.,
                           'swapped_wh_detected': True})

    interior = floats([[[16, 16], [48, 32], [80, 64]]])
    explicit = matcher_module.normalize_keypoints(interior, floats([[128, 96]]))
    fallback = matcher_module.normalize_keypoints(interior)
    require(not torch.equal(explicit, fallback), 'point-extent fallback is not image size')

    padded_cases = []
    for h, w in ((1280, 720), (129, 163)):
        # Integers stay below 2**24. Clamp-index reference does not call F.pad.
        require(h*w < 2**24, 'integer reference outside exact float32 range')
        source = torch.arange(h*w, dtype=torch.float32, device='cpu').reshape(1, 1, h, w)
        extra_y, extra_x = (-h) % 32, (-w) % 32
        top, left = extra_y//2, extra_x//2
        bottom, right = extra_y-top, extra_x-left
        ys = torch.arange(-top, h+bottom, device='cpu').clamp(0, h-1)
        xs = torch.arange(-left, w+right, device='cpu').clamp(0, w-1)
        reference = (ys[:, None]*w+xs[None, :]).to(torch.float32)[None, None]
        padder = aliked_module.InputPadder(h, w, 32)
        padded = padder.pad(source)
        exact(padded, reference, 'replicate padding reference: all edges/corners')
        exact(padder.unpad(padded), source, 'native padding roundtrip')
        padded_cases.append({'input_hw': [h, w], 'padded_hw': list(padded.shape[-2:]),
                             'padding_lrtb': [left, right, top, bottom],
                             'replicate_max_abs_value_error': 0.})

    # Centre-only dyadic kernel makes every product/sum exactly representable.
    image = torch.arange(126, dtype=torch.float32, device='cpu').reshape(1, 2, 7, 9)/8
    weights = torch.zeros((3, 2, 3, 3), dtype=torch.float32, device='cpu')
    weights[:, :, 1, 1] = floats([[.5, .25], [.125, .25], [-.5, .125]])
    bias = floats([.25, -.5, 1.])
    offsets = torch.zeros((1, 18, 7, 9), dtype=torch.float32, device='cpu')
    ordinary = torch.nn.functional.conv2d(image, weights, bias=bias, padding=1)
    deformed = aliked_module.torchvision.ops.deform_conv2d(
        image, offsets, weights, bias=bias, padding=(1, 1))
    exact(deformed, ordinary, 'zero-offset CPU deformable convolution')

    scores = torch.full((1, 4, 5), -16., dtype=torch.float32, device='cpu')
    scores[0, 0, 2] = scores[0, 2, 0] = 0.
    m0, m1, s0, s1 = matcher_module.filter_matches(scores, .5)
    exact(m0, torch.tensor([[2, -1, 0]], device='cpu'), 'source-to-target indices')
    exact(m1, torch.tensor([[2, -1, 0, -1]], device='cpu'), 'target-to-source indices')
    exact(s0, floats([[1, 0, 1]]), 'mutual source scores')
    exact(s1, floats([[1, 0, 1, 0]]), 'mutual target scores')
    target = floats([[10, 20], [30, 40], [50, 60], [70, 80]])
    valid = m0[0] >= 0
    exact(target[m0[0, valid]], floats([[50, 60], [10, 20]]), 'gather only valid targets')
    require(bool(torch.equal(target[m0[0, ~valid]], target[-1:])),
            'negative index would silently alias last target')

    empty = matcher_module.filter_matches(torch.full_like(scores, -16.), .5)
    require(bool((empty[0] == -1).all() and (empty[1] == -1).all()), 'no accepted matches')
    require(bool(((empty[2] > 0) & (empty[0] == -1)).any()),
            'positive score alone must not admit an unmatched index')
    # Raw filter has empty-axis max reductions; the model guards this separately.
    for shape in ((1, 1, 5), (1, 4, 1)):
        try:
            matcher_module.filter_matches(torch.zeros(shape, dtype=torch.float32, device='cpu'), .5)
        except (IndexError, RuntimeError):
            continue
        raise AssertionError('raw filter unexpectedly accepted a zero keypoint axis')

    return {'status': 'TECHNICAL_CHECK_PASSED', 'batch': 1, 'device': 'cpu', 'dtype': 'float32',
            'scope': 'owned software operators/coordinates/indices only; not physical pixel/mm precision',
            'numeric_basis': 'exact dyadic coordinates/kernel sums and integer padding; no physical tolerance',
            'normalization': normalized, 'extent_fallback_differs': True, 'padding': padded_cases,
            'deform_zero_offset_max_error': 0., 'source_target_counts': [3, 4],
            'matches0': m0.tolist(), 'matches1': m1.tolist(), 'unmatched_negative_index_guard': True,
            'all_unmatched_filter_case': True, 'positive_unmatched_score_detected': True,
            'raw_filter_zero_axis': 'unsupported reduction checked; model empty-input path not exercised',
            'models_loaded': False, 'model_inference': False}
