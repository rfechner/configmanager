from ._structs import BaseDict, AttributeDict, ImmutableAttributeDict, recursive_objectify
from ._load import load
from ._eval import apply_map
from ._parse import parse, tree_get, tree_put, contains_key
from ._config import AXIS_KEY

import sys
from typing import *
from itertools import product
from pathlib import Path
from typing import List

def load_config(path : Path | str, make_immutable=False) \
    -> List[AttributeDict | ImmutableAttributeDict]:
    """
        Main api entry point function. Loads a nested dictionary,
        handles imports, string interpolation and expands grid search
        axes.

        Usage:

        ```python
        >>> configs = load_config('path/to/conf.yaml')
        >>> [AttributeDict(...), AttributeDict(...), ...]
        ```
    """

    if isinstance(path, str):
        path = Path(path)

    d : dict = load(path)
    config : dict = parse(current=d, curdepth=0)

    config : dict = apply_map(current=config, global_config=config)
    found_axis_key = contains_key(config, key=AXIS_KEY)
    configs : List[Dict] = [config] 

    while found_axis_key:

        updated_configs = []
        for config in configs:
            if not contains_key(config, key=AXIS_KEY):
                updated_configs.append(config)
                continue
            
            # get the grid axes
            axes : List[List[Any]] = tree_get(node=config, key=AXIS_KEY)
            products : Generator[List[List[Any]]] = product(*axes)
            
            # insert different constellations into base config
            update : List[Dict] = [
                tree_put(node=config, key=AXIS_KEY, swaps=list(entry)) \
                    for entry in products
            ]
            updated_configs.extend(update)
            
        # test if we need to iterate
        configs = updated_configs
        found_axis_key = any([
            contains_key(config, key=AXIS_KEY) for config in configs
        ])
                
    # turn dicts into objects
    configs : List[AttributeDict | ImmutableAttributeDict] = \
        [recursive_objectify(config, make_immutable=make_immutable) \
            for config in configs]
    
    return configs