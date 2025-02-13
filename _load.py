from pathlib import Path
import json
import yaml


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
    """
        Main entry point to load any config. See valid_suffixes for
        accepted file formats.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
        
    suffix = filepath.suffix
    assert suffix in valid_suffixes.keys(), \
        f"Tried to load file in unsupported format: {str(filepath)}, Supported filetypes: {valid_suffixes.keys()}"

    return valid_suffixes[suffix](filepath)    