"""Fast stdlib regression tests; no scientific arrays are recomputed or replaced."""
from pathlib import Path
from unittest.mock import patch
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
import unittest

PHYSICS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PHYSICS))
import provenance
import reproduce


def load(name):
    spec=importlib.util.spec_from_file_location(f'safety_{name}',PHYSICS/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def dependency_stubs():
    def forbidden(*args,**kwargs):raise AssertionError('A fail-closed check reached a scientific solve')
    modules={name:types.ModuleType(name) for name in ['numpy','scipy','scipy.special','scipy.interpolate','shapely','shapely.geometry','model','bem','generate']}
    modules['scipy.special'].ellipk=forbidden
    modules['scipy.interpolate'].PchipInterpolator=forbidden
    modules['shapely.geometry'].Polygon=forbidden
    model=modules['model'];model.P={'angle_scan_deg':[]}
    for key in ['polygons','upper','analytic']:setattr(model,key,forbidden)
    modules['bem'].Solution=forbidden
    modules['generate'].fieldmap=forbidden;modules['generate'].trace=forbidden
    return modules


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='mutual-safety-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ['physics','data','qa','source/src/physics']:(self.root/name).mkdir(parents=True,exist_ok=True)
        (self.root/'parameters.json').write_text('{"note":"参数"}',encoding='utf-8')
        (self.root/'physics/placeholder.py').write_text('# test runner',encoding='utf-8')
        self.expected=provenance.parameter_hash(self.root)
        self.dataset={'parameterSha256':self.expected,'er_scan':[],'provenance':{}}
        self.write('data/results.json',self.dataset)
        (self.root/'source/src/physics/data.ts').write_text('frozen TS',encoding='utf-8')
        self.write('qa/historical.json',{'legacy':'retained'})
        self.before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def write(self,name,data):
        (self.root/name).write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')

    def assert_unchanged(self):
        after={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(after,self.before)

    def checkpoints(self,hash_value=None,complete=True):
        for name in ['finite-width-3d.json','independent-fvm.json']:
            self.write(f'qa/{name}',{'parameterSha256':hash_value or self.expected,'complete':complete,'rows':[{'test':1}]})

    def test_failed_validation_blocks_generate_before_solves_and_writes(self):
        with patch.dict(sys.modules,dependency_stubs()):module=load('generate')
        module.ROOT=self.root
        for checks in [[],[{'name':'collision','passed':False}],[{'passed':1}]]:
            module.validation=lambda:{'checks':checks,'parameterSha256':self.expected}
            with self.assertRaisesRegex(ValueError,'generation blocked'):module.main()
            self.assert_unchanged()

    def test_enrich_rejects_missing_legacy_and_mismatched_checkpoint_hash(self):
        with patch.dict(sys.modules,dependency_stubs()):module=load('enrich')
        module.R=self.root
        self.checkpoints()
        for name in ['finite-width-3d.json','independent-fvm.json']:
            for record in [{'complete':True,'rows':[{}]},{'parameterSha256':'old','complete':True,'rows':[{}]},{'parameterSha256':self.expected,'complete':False,'rows':[{}]}]:
                self.checkpoints();self.write('qa/'+name,record)
                original=(self.root/'data/results.json').read_bytes()
                with self.assertRaises(ValueError):module.main()
                self.assertEqual((self.root/'data/results.json').read_bytes(),original)
                self.assertEqual((self.root/'source/src/physics/data.ts').read_text(encoding='utf-8'),'frozen TS')

    def test_dataset_must_match_current_utf8_parameters(self):
        self.assertEqual(provenance.load_dataset(self.root),self.dataset)
        self.write('parameters.json',{'changed':True})
        with self.assertRaises(ValueError):provenance.load_dataset(self.root)

    def runner(self,command,cwd,check):
        self.assertTrue(check);stage=Path(cwd)
        self.assertNotEqual(stage,self.root)
        self.assertEqual(provenance.parameter_hash(stage),self.expected)
        if Path(command[1]).name==reproduce.STAGES[-1]:
            for name in ['finite-width-3d.json','independent-fvm.json']:
                (stage/'qa'/name).write_text(json.dumps({'parameterSha256':self.expected,'complete':True,'rows':[{}]}),encoding='utf-8')
            (stage/'qa/numerical-validation.json').write_text(json.dumps({'parameterSha256':self.expected,'checks':[{'passed':True}]}),encoding='utf-8')
            (stage/'qa/interpolation-check.json').write_text(json.dumps({'parameterSha256':self.expected}),encoding='utf-8')
            (stage/'data/results.json').write_text(json.dumps({**self.dataset,'fresh':True}),encoding='utf-8')
            (stage/'source/src/physics/data.ts').write_text('fresh TS',encoding='utf-8')

    def test_failed_stage_leaves_frozen_outputs_and_historical_qa_untouched(self):
        def fail(command,cwd,check):
            (Path(cwd)/'data/results.json').write_text('partial stage',encoding='utf-8')
            raise subprocess.CalledProcessError(1,command)
        with self.assertRaises(subprocess.CalledProcessError):reproduce.reproduce(self.root,fail)
        self.assert_unchanged()

    def test_success_publishes_only_after_all_stages(self):
        reproduce.reproduce(self.root,self.runner)
        self.assertTrue(json.loads((self.root/'data/results.json').read_text(encoding='utf-8'))['fresh'])
        self.assertEqual((self.root/'source/src/physics/data.ts').read_text(encoding='utf-8'),'fresh TS')
        self.assertEqual(json.loads((self.root/'qa/historical.json').read_text(encoding='utf-8')),{'legacy':'retained'})

    def test_missing_output_or_parameter_change_cannot_publish(self):
        for failure in ['missing','parameters','validation']:
            def runner(command,cwd,check):
                self.runner(command,cwd,check)
                if Path(command[1]).name==reproduce.STAGES[-1]:
                    stage=Path(cwd)
                    if failure=='missing':(stage/'source/src/physics/data.ts').unlink()
                    elif failure=='parameters':(stage/'parameters.json').write_text('{}',encoding='utf-8')
                    else:(stage/'qa/numerical-validation.json').write_text(json.dumps({'parameterSha256':self.expected,'checks':[{'passed':False}]}),encoding='utf-8')
            with self.assertRaises((ValueError,FileNotFoundError)):reproduce.reproduce(self.root,runner)
            self.assert_unchanged()

    def test_publication_error_rolls_back_previously_replaced_outputs(self):
        real_replace=reproduce.os.replace;count=0
        def fail_second(source,target):
            nonlocal count
            count+=1
            if count==2:raise OSError('synthetic write failure')
            return real_replace(source,target)
        with patch.object(reproduce.os,'replace',fail_second):
            with self.assertRaises(OSError):reproduce.reproduce(self.root,self.runner)
        self.assert_unchanged()


if __name__=='__main__':unittest.main()
