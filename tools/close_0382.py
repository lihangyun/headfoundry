"""Archive only the bounded generic control; never touches patient material."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
src=root/'assets/private/render-conditioned-0382'
dst=root/'assets/private/closed-experiments/0382-render-conditioned'
dst.mkdir(exist_ok=False)
files=sorted(src.iterdir())
assert all(p.is_file() and not p.is_symlink() for p in files)
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
archive=dst/'evidence.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,item in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==item['sha256']
print(json.dumps({'files':len(files),'bytes':sum(x['bytes'] for x in manifest.values()),'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifest':manifest},indent=2))
