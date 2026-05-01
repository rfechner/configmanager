import re
import ast

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
    if isinstance(current, str):
        matches = re.findall(SINTERP_PATTERN, current)
        if matches:
            replacements = [sinterp(m, global_config) for m in matches]
            ret = multi_replace(current, replacements, SINTERP_PATTERN)
            # re.sub always returns a string; evaluate back to the original type for single non-str replacements
            if (len(replacements) == 1) and not isinstance(replacements[0], str):
                ret = ast.literal_eval(ret)
            return ret
    elif isinstance(current, LeafType):
        pass
    elif isinstance(current, list):
        return [apply_map(v, global_config=global_config) for v in current]
    elif isinstance(current, dict):
        return {
            apply_map(k, global_config=global_config): apply_map(v, global_config=global_config)
            for k, v in current.items()
        }
    else:
        raise TypeError(f"Encountered Error while trying to parse value: {current} of type {type(current)}")
    return current

