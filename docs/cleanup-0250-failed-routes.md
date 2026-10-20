# Cleanup0250: retire failed routes before new experiments

Date:2026-10-20. User-authorized cleanup,not a new reconstruction experiment.
No head/camera/likeness promotion and no new modeling run.

## Scope and intent

Retire failed model-specific workflows rather than leave hundreds of runners,
tests,heads,renders and environments active. Keep original inputs/consent,
successful evaluation fixtures,shared numerical/rights/safety tests and readable
failure conclusions. Tests of a failed route are not the same as generic tests
of correct shared math;the latter stay. No source module or production default
is changed by this cleanup. There is still no accepted reconstructed head.

Historical source recovery point:`d443e37`. All earlier experiment documents
remain historical evidence;their commands/large output links may now refer to
retired files. Do not silently reinstall the rejected routes from these docs.

## Removed from the active tree

- 79 experiment-specific tools from0208-0249 and older DA3,MapAnything,XFeat,
  LighterGlue/COLMAP integration runners;33 failed-route-only test files.
- Seven obsolete example locks for those integrations.
- Public DA3/MapAnything/GNM/MoGe/TripoSR/XFeat source and weight downloads,
  duplicate/partial downloads and obsolete converted shape-basis experiments.
- Generated failed heads,predictions,diagnostic renders and old subject001
  experiment scripts;failed real-case pilot branches. Successful fixed scan
  reference/upright known-motion benchmark and their evaluation fixtures stay.
- The isolated .venv-recon and Gaussian-splat environment,plus their dependency
  caches. The tiny runtime interpreter directory is retained because it contains
  a reparse link;no linked external directory is traversed or removed.
- Seventeen no-longer-referenced model packages from the main project venv,
  including Torch/TorchVision,timm,UniCeption,pycolmap,Kornia and model-download
  support. Retained code has no live dependency on these packages.

Generic depth projection and contact-expression regressions are retained while
removing their dependencies on retired runner code. Generic depth math in
`src/headfoundry/da3.py` remains because shared fusion uses it;the filename does
not imply a retained DA3 model integration.

## Private evidence and recovery limits

Private index:`assets/private/cleanup-0250/plan.json`,archive-inventory.json,
protected-hashes.json,environments-before.json and execution/verification records.
Compact `failure-evidence.zip` is6173822bytes,982 evidence files,CRC verified;
SHA256=`fe05789daa100e7f0bcbc9a9141933f41f3f9255a4d279bc1044142414773f6f`.
It preserves reports/controls/logs/license records and a few representative
0241/0246/0249 comparisons,not full failed meshes or checkpoints. It stays
local and outsideGit because it can contain sensitive validation metadata.

Exact prevalidated deletion list:715 targets,82698 files,41152226871bytes
(41.15decimalGB/38.33GiB,logical file sizes,not independently measured free-disk
gain). Package-uninstall bytes are not included. No destructive target is the
workspace root;all resolved paths are checked inside this repository,reparse
targets refused,and archive integrity checked before deletion.

Tracked source/tests are recoverable from Git. Deleted public weights must be
downloaded again at their recorded hashes;deleted generated binaries require
reexecution from historical source and original local inputs. The compact
archive cannot restore those binaries byte-for-byte. No files are uploaded.

## Protected and intentionally untouched

Original five authorized photos and run-manifest,real-case consent/provenance,
the real-case input review and sampled frames,external original videos/skin/bone
STLs,FLAME source/converted asset,raw CC0 prior,MediaPipe and Blender/common
rendering tools remain. case002 is not opened for evaluation or tuning.

Pre-existing untracked `docs/experiment-0207-coupled-lip-and-jaw.md` is untouched.
Unclassified root/NVIDIA and tmp material,including vendor-investigation folders,
is not assumed to be disposable failed output;it is neither read nor deleted.
This cleanup covers the positively identified failed routes,not every untracked
file or every scientific library in the repository.

## Ongoing rule

Project [AGENTS.md](../AGENTS.md) requires:record rejection and recovery point,
archive minimal private evidence,remove exclusive failed-route code/assets/
frameworks,verify protected inputs and shared tests,commit closeout,then start
the next pre-registered route. This replaces the old policy of retaining every
failed binary indefinitely;it does not authorize deleting original inputs or
accepted baselines. Failed-route counts/test totals are historical,not current
coverage claims. A smaller remaining test suite is not an algorithm improvement.

## Actual closeout verification

127 retained unit tests pass in4.591s;the previous207 included retired-route
tests. `uv --no-cache pip check` passes for the main environment. Generic input,
rights,camera,scan,mesh and quality tests remain. Shared package source and
production defaults are unchanged. Final protected-file hashes,deletion absence
checks,archive CRC/SHA and Git whitespace checks are recorded privately.
Historical PCR handoff/location snapshots under artifacts remain snapshots;
their failed-output paths are not a promise those deleted files still exist.
