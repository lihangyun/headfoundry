# 0374 isolated metric Small runtime

2026-10-27 engineering preparation,not a reconstruction experiment.
Use project-local .venv-metric0374, no main-venv change. OfficialPyTorch
previous-version page pairs torch2.8.0/torchvision0.23.0 CUDA12.6 forWindows:
https://pytorch.org/get-started/previous-versions/ . No torchaudio needed.
Pin numpy2.2.6,opencv-python4.12.0.88,pillow11.3.0; no UI/Open3D/training.
Only binary packages,officialPyTorch andPyPI indices,no pipcache,userinstall
or globaltemporary writes. Capturepip JSONreports,fullfreeze,installedlicense
metadata and license-file hashes before admitting runtime. Runtime import or
license problems are engineering failures,not model accuracy failures.
Setup budget900s/4GiBprocessworkingmemory. Download/disk cost may be severalGB;
stop if installation fails rather than trying a chain of alternate versions.
No patient inputs,inference,training or production defaults changed. Source
and checkpoint remain pinned by0373; modelimport deferred until dependency
and source review complete. This step does not license every binary merely
because the top-level package is open source.
