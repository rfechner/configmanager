import re

from copy import deepcopy
from _structs import *

from _config import SINTERP_PATTERN

def extract(string : str, pattern : str = SINTERP_PATTERN) -> Optional[str]:
    match = re.match(pattern=pattern, string=string)
    if not match:
        return None
    return match.group(1)

def sinterp(string : str, config : Dict) -> NodeType | LeafType:
    parts = string.split('.')
    subconf = config
    for part in parts:
        subconf = subconf[part]
    return subconf

def apply_map(current : Any, global_config : dict) -> Any:
    copy = deepcopy(current)
    if isinstance(current, str):
        match = extract(copy)
        if match:
            return sinterp(string=match, config=global_config)
        else:
            pass
    elif isinstance(current, LeafType):
        pass
    elif isinstance(current, list):
        copy = [
            apply_map(v, global_config=global_config) for v in current
        ]
    elif isinstance(current, dict):
        copy = {
            apply_map(k, global_config=global_config) : \
                apply_map(v, global_config=global_config) for k, v in current.items() 
        }
    else:
        raise TypeError(f"Encountered Error whily trying to parse value: {current} of type {type(config)}")
    
    return copy

