"""Regenerate in isolation, publish only after every scientific stage succeeds."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
from provenance import parameter_hash,require_parameters,require_validation,read_checkpoint

ROOT=Path(__file__).resolve().parents[1]
STAGES=['trial_and_validate.py','fvm_check.py','bem3d_check.py','generate.py','enrich.py','local_maps.py','check_interpolation.py']


def publish(stage,root):
    paths=[Path('data/results.json'),Path('source/src/physics/data.ts')]
    paths.extend(path.relative_to(stage) for path in sorted((stage/'qa').glob('*.json')))
    # Read all outputs before touching the previous delivery.
    outputs={path:(stage/path).read_bytes() for path in paths}
    previous={path:(root/path).read_bytes() if (root/path).exists() else None for path in paths}
    changed=[]
    try:
        for path,content in outputs.items():
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as handle:
                temporary=Path(handle.name);handle.write(content)
            try:
                os.replace(temporary,target);changed.append(path)
            finally:
                temporary.unlink(missing_ok=True)
    except Exception:
        for path in reversed(changed):
            if previous[path] is None:(root/path).unlink(missing_ok=True)
            else:(root/path).write_bytes(previous[path])
        raise


def reproduce(root=ROOT,runner=subprocess.run):
    root=Path(root).resolve();expected=parameter_hash(root)
    with tempfile.TemporaryDirectory(prefix='capacitance-reproduce-') as directory:
        stage=Path(directory)
        shutil.copytree(root/'physics',stage/'physics',ignore=shutil.ignore_patterns('__pycache__','tests'))
        shutil.copy2(root/'parameters.json',stage/'parameters.json')
        for path in ['qa','data','source/src/physics']:(stage/path).mkdir(parents=True,exist_ok=True)
        for name in STAGES:
            print('RUN',name,'(staging)',flush=True)
            runner([sys.executable,str(stage/'physics'/name)],cwd=stage,check=True)
        if parameter_hash(root)!=expected or parameter_hash(stage)!=expected:
            raise ValueError('parameters.json changed during reproduction; publishing blocked')
        validation=json.loads((stage/'qa/numerical-validation.json').read_text(encoding='utf-8'))
        require_parameters(validation,expected,'numerical-validation');require_validation(validation)
        for name in ['finite-width-3d.json','independent-fvm.json']:
            read_checkpoint(stage/'qa'/name,expected)
        data=json.loads((stage/'data/results.json').read_text(encoding='utf-8'))
        require_parameters(data,expected,'results')
        interpolation=json.loads((stage/'qa/interpolation-check.json').read_text(encoding='utf-8'))
        require_parameters(interpolation,expected,'interpolation-check')
        publish(stage,root)
    print('Regenerated SI data. Run npm run build in source to rebuild the HTML.',flush=True)


if __name__=='__main__':reproduce()
