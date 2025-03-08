import re

from copy import deepcopy
from ._structs import *

from ._config import SINTERP_PATTERN

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

def multi_replace(text, replacements, pattern):
    # Create an iterator over the replacements
    repl_iter = iter(replacements)

    # Use re.sub with a lambda that returns the next replacement
    return re.sub(pattern, lambda match: str(next(repl_iter)), text)

def apply_map(current : Any, global_config : dict) -> Any:
    copy = deepcopy(current)
    if isinstance(current, str):
        matches = re.findall(SINTERP_PATTERN, current)
        if matches:
            # turn matches into corresponding strings
            replacements = [sinterp(m, global_config) for m in matches]
            ret = multi_replace(current, replacements, SINTERP_PATTERN)

            # in case ret is a single primitive, it's interpreted by re.sub as a string.
            # hence, we have to evaluate the string in case it isn't.
            if (len(replacements) == 1) and not isinstance(replacements[0], str):
                ret = eval(ret)

            return ret
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
        raise TypeError(f"Encountered Error whily trying to parse value: {current} of type {type(current)}")
    
    return copy

