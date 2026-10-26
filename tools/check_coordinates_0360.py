"""Owned analytical grid tests; no learned-model or patient evaluation."""
import json
from pathlib import Path
import torch
from trackon_local_0359 import indices_to_coords


def main():
    ids = torch.tensor([[0, 1, 2], [3, 4, 5]])
    actual = indices_to_coords(ids, (8, 12), 4)
    expected = torch.tensor([[[2.,2.],[6.,2.],[10.,2.]], [[2.,6.],[6.,6.],[10.,6.]]])
    assert torch.equal(actual, expected)
    assert indices_to_coords(torch.empty((2,0), dtype=torch.int64), (8,12), 4).shape == (2,0,2)
    rejected = 0
    for indices, size, stride in [(torch.tensor([-1]), (8,12), 4),
                                  (torch.tensor([6]), (8,12), 4),
                                  (torch.tensor([0.]), (8,12), 4),
                                  (torch.tensor([0]), (9,12), 4),
                                  (torch.tensor([0]), (8,12), 0)]:
        try:
            indices_to_coords(indices, size, stride)
        except ValueError:
            rejected += 1
    assert rejected == 5
    # Match align_corners=False feature sampling: cell centers recover cells exactly.
    field = torch.arange(6, dtype=torch.float32).reshape(1,1,2,3)
    normalized = actual.reshape(1,6,1,2) / torch.tensor([12.,8.]) * 2 - 1
    samples = torch.nn.functional.grid_sample(field, normalized, align_corners=False)
    error = float((samples.flatten() - torch.arange(6)).abs().max())
    assert error < 1e-6
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="independent coordinate arithmetic",
                  rejected_invalid_inputs=rejected, feature_sampling_error=error,
                  trained_model_convention="UNVERIFIED", model_forward="NOT_RUN")
    out = Path(__file__).resolve().parents[1] / "assets/private/trackon-coordinates-0360"
    out.mkdir(parents=True, exist_ok=True)
    (out / "controls.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
