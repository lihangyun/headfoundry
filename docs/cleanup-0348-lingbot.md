# 0348 cleanup: fixed LingBot camera recipe retired

2026-10-24. Physical result REJECT; see experiment-0348-lingbot-owned-camera.md.
Source recovery692739f; exact scoped cleanup implementation6b4b3b6.
No further inference,patient fitting,medical comparison or new route here.

Private archive:assets/private/closed-experiments/0348-lingbot/evidence.zip.
5,388,789bytes; SHA256750c7b749e065baab1a8b409fd556e9863194129ca6de1d5cde5f2b780257c48.
CRC and every member hash checked. It contains raw camera/depth/confidence,
all point errors/support,model/source identities,source/license snapshots and
acquisition/load/evaluation logs. audit.json records numerical controls and
archive inventory;cleanup.json records deletion targets/counts and process checks.

Removed four exact directories inside this repository:lingbot-source-0346,
lingbot-entry-0347,lingbot-physical-0348 under assets/private,and
.venv-lingbot-0347. Their38,044files total19,948,216,623logical bytes;this is
not a measured physical disk-space gain (environment/cache can use hard links).
Each resolved path was checked within its explicit root;reparse points were
refused. Recorded worker PIDs were absent before deletion.112 protected inputs,
consent records and successful fixtures matched their prior hashes both before
and after. Originals,0332fixture,case002,main environment and0207remain untouched.

Removed nine exclusive tracked tools/tests and five identified bytecode files.
No live LingBot references remain in tools/tests. Generic pinhole math,resource
monitor and all shared evaluation/rights/safety code remain.163remaining tests
pass in9.323s;main environment39packages compatible. No production change.

Recovery:Git restores scripts,not deleted checkpoints or runtime binaries.
Public weights require downloading at recorded identity;environment/cache must
be rebuilt. Compact evidence is not a complete binary installation backup.
Do not automatically restore or sweep this failed recipe. No accepted head exists.
