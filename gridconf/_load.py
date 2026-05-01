from pathlib import Path
import json
import yaml
import sys

def load_yaml(path : Path):
    with open(path, 'r') as file:
        ret = yaml.safe_load(file)
    return ret

def load_json(path : Path):
    with open(path, 'r') as file:
        ret = json.load(file)
    return ret

valid_suffixes = {'.yaml': load_yaml, 
                  '.yml' : load_yaml,
                  '.json' : load_json}

def load(filepath : str | Path):
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if filepath.is_absolute():
        if not filepath.exists():
            raise ValueError(f"Couldn't find file: {filepath}")
        total_path = filepath
    else:
        total_path = None
        for directory in sys.path:
            candidate = Path(directory) / filepath
            if candidate.exists():
                total_path = candidate
                break
        if total_path is None:
            raise ValueError(f"Couldn't find file: {filepath} in pythonpath!")

    assert total_path.suffix in valid_suffixes, \
        f"Tried to load file in unsupported format: {total_path}, Supported filetypes: {list(valid_suffixes)}"

    return valid_suffixes[total_path.suffix](total_path)