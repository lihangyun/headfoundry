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

## Original in-progress handoff (superseded below)

Setup registered6d9d0d1; installation worker started and remained live on
session4434 at this handoff. Do not start another setup from a stale record:
poll that handle first. Runtime completion/rights/import status UNVERIFIED.
The current download is the official2915.4MBtorch CUDAwheel; no model inference
started. Controller enforces900s deadline. Log/receipt live under
assets/private/metric-runtime-0374/worker.log and worker.json.
Pinned inference source independently fetched:16files78591bytes,all hashes
recorded in source/manifest.json. Only metric_depth/depth_anything_v2 Python
files and license/readme/requirements fetched; no vendor install script run.
DINOv2 constructor builds modules without external checkpoint downloads;
attention has a nativeTorch fallback when optionalxformers is absent. Do not
installxformers to silence its warning or change the registered precision.
Main environment and unrelated0207 were not modified. Before inference,review
installedlicense evidence and runtime report,then strictweights_only loading
of0373hash. Do not equate the source fetch with physical capacity acceptance.

## Installation completion and offline check, 2026-10-27

Terminal receipt confirms exit0 in487.984s,conservative process-tree peak
1100431360bytes. Do not restart the installer. Imports report torch2.8.0+cu126,
torchvision0.23.0+cu126,opencv4.12.0,numpy2.2.6 and CUDA available.
Installed license inventory exists but is NOT a completed transitive binary
license review; runtime admission remains UNVERIFIED. No inference has run.

Next engineering check is offline only: verify all16source bytes against their
saved manifest, fixed checkpoint size/SHA and archive CRCs without unpickling,
executing vendor code or using patient inputs. Corrupt bytes,wrong size and
escaping manifest paths must fail. This check is not model-architecture matching
or a new accuracy experiment. Main environment and production remain unchanged.

Actual offline check:16files verified,checkpoint241archive members CRC-valid;
all three negative controls passed. Receipt bundle-integrity.json records
TECHNICAL_CHECK_PASSED solely for integrity,license/accuracyUNVERIFIED and
inferenceNOT_RUN. Reproduce with tools/check_metric_bundle_0374.py using the
main Python environment (standard library only; no inference dependencies).
Regression verification:167shared tests pass in9.974s; git diff whitespace
check passes. These tests do not validate the new network's physical accuracy.
