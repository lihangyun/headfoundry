# Copyright 2025 The HuggingFace Team. All rights reserved.
# Copyright 2026 HeadFoundry contributors.
# Licensed under the Apache License, Version 2.0.
# https://www.apache.org/licenses/LICENSE-2.0
# Distributed WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
# Modified from the pinned HF EfficientLoFTR parameter-free index routines:
# preserve aligned source/target pairs and gather on the fine-window axis.
"""Experiment0274 only; no learned parameters or changed matching thresholds."""
import torch
from transformers import EfficientLoFTRForKeypointMatching
from transformers.models.efficientloftr.modeling_efficientloftr import create_meshgrid


class AlignedIndexMatcher(EfficientLoFTRForKeypointMatching):
    def _get_matches_from_scores(self, scores):
        maps, confidence = super()._get_matches_from_scores(scores)
        target = maps[:, 1]
        source = torch.arange(target.shape[1], device=target.device).expand_as(target)
        source = torch.where(target >= 0, source, -1)
        return torch.stack([source, target], dim=1), confidence[:, 1:2].expand(-1, 2, -1)

    def _get_first_stage_fine_matching(self, fine_confidence, coarse_matched_keypoints,
                                       fine_window_size, fine_scale):
        batch, count = fine_confidence.shape[:2]
        kernel = int(fine_window_size ** .5)
        index = fine_confidence.reshape(batch, count, -1).max(dim=-1).indices[..., None]
        first, second = index // fine_window_size, index % fine_window_size
        grid = create_meshgrid(kernel, kernel, normalized_coordinates=False,
                               device=fine_confidence.device, dtype=fine_confidence.dtype)
        grid = (grid - kernel // 2 + .5).reshape(1, 1, -1, 2).expand(batch, count, -1, -1)
        delta0 = torch.gather(grid, 2, first.unsqueeze(-1).expand(-1, -1, -1, 2)).squeeze(2)
        delta1 = torch.gather(grid, 2, second.unsqueeze(-1).expand(-1, -1, -1, 2)).squeeze(2)
        points = torch.stack([coarse_matched_keypoints[:, 0] + delta0 * fine_scale,
                              coarse_matched_keypoints[:, 1] + delta1 * fine_scale], dim=1)
        return torch.stack([first, second], dim=1), points


def check_actual_contracts(model):
    score = torch.zeros((1, 81, 81))
    score[0, [30, 31, 39], [31, 39, 30]] = torch.tensor([.9, .8, .7])
    pairs, confidence = model._get_matches_from_scores(score.reshape(1, 9, 9, 9, 9))
    eligible = (confidence[0] > .2).all(dim=0)
    actual = pairs[0, :, eligible].T
    expected = torch.tensor([[30, 31], [31, 39], [39, 30]])
    if not torch.equal(actual, expected):
        raise ValueError('Actual Torch override lost interior pair identities')
    count = 81
    source = (torch.arange(162).reshape(2, count) * 13 + 7) % 64
    target = (torch.arange(162).reshape(2, count) * 17 + 3) % 64
    fine = torch.zeros((2, count, 64, 64))
    fine[torch.arange(2)[:, None], torch.arange(count)[None, :], source, target] = 1
    coarse = torch.zeros((2, 2, count, 2))
    _, actual_fine = model._get_first_stage_fine_matching(fine, coarse, 64, 1.25)
    expected_fine = torch.stack([torch.stack([source % 8 - 3.5, source // 8 - 3.5], -1),
                                 torch.stack([target % 8 - 3.5, target // 8 - 3.5], -1)], 1) * 1.25
    if not torch.equal(actual_fine, expected_fine):
        raise ValueError('Actual Torch override differs from enumerated fine cells')
    return {'status': 'TECHNICAL_CHECK_PASSED', 'true_coarse_pairs': 3,
            'fine_pairs_checked': 162, 'fine_max_error': 0,
            'scope': 'Actual parameter-free routines only, not full-model batching or physical accuracy'}

