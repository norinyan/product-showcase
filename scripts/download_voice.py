"""Download the example's pinned voice, verify hashes; weights stay outside Git."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',default='.models');a=p.parse_args();m=json.loads(Path(a.manifest).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
base=f'https://huggingface.co/{m["repository"]}/resolve/{m["revision"]}/'
for suffix,key in [('', 'sha256'),('.json','config_sha256')]:
 remote=m['path']+suffix;path=out/Path(remote).name
 if not path.exists()or hashlib.sha256(path.read_bytes()).hexdigest()!=m[key]:
  temp=path.with_suffix(path.suffix+'.part');urllib.request.urlretrieve(base+remote,temp)
  if hashlib.sha256(temp.read_bytes()).hexdigest()!=m[key]:temp.unlink();raise ValueError('Voice hash mismatch')
  temp.replace(path)
 print(path)
