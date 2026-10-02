"""Fail-closed parameter and checkpoint provenance for fresh reproductions."""
from pathlib import Path
import hashlib
import json


def parameter_hash(root):
    return hashlib.sha256((Path(root) / 'parameters.json').read_bytes()).hexdigest()


def require_parameters(record, expected, label):
    if not expected or record.get('parameterSha256') != expected:
        raise ValueError(f'{label}: missing or mismatched parameterSha256; regenerate evidence')


def require_validation(record):
    checks = record.get('checks')
    if not checks or any(check.get('passed') is not True for check in checks):
        failed = [check.get('name', '<unnamed>') for check in checks or [] if check.get('passed') is not True]
        raise ValueError(f'Numerical validation failed; generation blocked: {failed or "missing checks"}')


def read_checkpoint(path, expected):
    record = json.loads(Path(path).read_text(encoding='utf-8'))
    require_parameters(record, expected, str(path))
    if record.get('complete') is not True or not record.get('rows'):
        raise ValueError(f'{path}: incomplete numerical checkpoint; regenerate evidence')
    return record


def load_dataset(root):
    data = json.loads((Path(root) / 'data/results.json').read_text(encoding='utf-8'))
    require_parameters(data, parameter_hash(root), 'data/results.json')
    return data
