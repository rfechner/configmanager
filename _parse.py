from typing import *
from ._load import load
from ._structs import *
from ._config import *
from ._eval import extract

from copy import deepcopy, copy



def recursive_update(current : dict, update : dict, curdepth : int, overwrite : bool = False) -> dict:
    """
        Recurses through the dictionary `update` and applies changes to
        a copy of `current`.
    """
    if curdepth > MAX_RECURSION_DEPTH:
        raise RecursionError
    
    ret = deepcopy(current)
    if not isinstance(current, dict):
        return ret
    
    for key, value in update.items():
        """
            Two cases:

            1) ret[key] and value are both dictionaries. In this case, we'd like
            to recursively apply recursive_update.

            2) multitude of sub-cases. For each of them, we just want to overwrite or set
            ret[key] to value.
        """
        
        if not overwrite and \
            key in ret.keys() and \
            (isinstance(ret[key], dict) and isinstance(value, dict)):

            ret[key] = recursive_update(ret[key], value, curdepth=curdepth + 1, overwrite=overwrite)
        else:
            ret[key] = value
    return ret

def contains_key(node : NodeType | LeafType, key : str) -> bool:
    found = False
    if isinstance(node, LeafType):
        pass
    elif isinstance(node, list):
        for subnode in node:
            if contains_key(subnode, key=key):
                found = True
                break
    elif isinstance(node, dict):
        if key in node.keys():
            found = True
        else:
            for v in node.values():
                if contains_key(v, key=key):
                    found = True
    else:
        raise TypeError(f"Encountered Error whily trying to parse value: {value} of type {type(value)}. Allowed types: {Union[LeafType, NodeType]}")

    return found

def parse(current : NodeType | LeafType, curdepth : int, overwrite : bool = False) -> Any:

    config = recursive_parse(current, curdepth, overwrite)

    # remove import and overwrite statements, as they should've already been executed.
    config = tree_remove(config, remove_key=IMPORT_KEY)
    config = tree_remove(config, remove_key=OVERWRITE_KEY)

    return config

def recursive_parse(current : NodeType | LeafType, curdepth : int, overwrite : bool = False) -> Any:
    """
        recurse through the current dictionary | leaftype.
        This implementation overwrites the subdictionaries by default.
    """
    if curdepth > MAX_RECURSION_DEPTH:
        raise RecursionError("Maximum recursion depth reached! Might have circular import!")
    
    ret = deepcopy(current)
    if isinstance(current, LeafType):
        pass # fall through
    elif isinstance(current, list):
        ret = [
            recursive_parse(v, curdepth = curdepth + 1) for v in current
        ]
    elif isinstance(current, dict):
        for key, value in current.items():

            # check if we should overwrite the sub-tree
            ckey = copy(key)
            match = extract(key, OVERWRITE_PATTERN)

            # overwrite should be carried down the recursion
            overwrite = overwrite or (match != None)
            key = match if match else key

            if match == IMPORT_KEY:
                raise ValueError("overwriting an import statement isn't supported.")
            
            if key == IMPORT_KEY:
                """
                    import statements can be either a single key, value pair
                    where the value is a string, or a list of import statements.
                """
                if isinstance(value, list):
                    imports = []
                    for importstmt in value:
                        imports.append(
                            recursive_parse(
                                load(importstmt), curdepth = curdepth + 1, overwrite=overwrite
                            )
                        )
                    del ret[key]
                    for update in imports:
                        ret = recursive_update(ret, update, curdepth = 1, overwrite=overwrite)

                elif isinstance(value, str):
                    update = recursive_parse(
                        load(value), curdepth = curdepth + 1, overwrite=overwrite
                    )

                    del ret[key]
                    ret = recursive_update(ret, update, curdepth = 1, overwrite=overwrite)
                else:
                    raise ValueError("Import Statements can only be a list of strings or a single string!")
            else:
                if match:
                    # we should delete the old `__overwrite__(key)` key
                    del ret[ckey]

                update = {
                    key : recursive_parse(
                    value, curdepth = curdepth + 1, overwrite=overwrite
                )}

                ret = recursive_update(ret, update, curdepth = 1, overwrite=overwrite)

    else:
        raise TypeError(f"Encountered Error whily trying to parse value: {value} of type {type(value)}. Allowed types: {Union[LeafType, NodeType]}")
    return ret

def tree_get(node : NodeType | LeafType, key : str) -> List[List[Any]]:

    ret = []
    if isinstance(node, LeafType):
        pass
    elif isinstance(node, list):
        for entry in node:
            ret.extend(
                tree_get(entry, key=key)
            )
    elif isinstance(node, dict):
        for key, value in node.items():
            if key == AXIS_KEY:
                ret.append(value)   # appends a list of grid items to found
                                    # stop recursion
            else:
                ret.extend(
                    tree_get(value, key=key)
                )
    else:
        raise TypeError(f"Encountered Error while trying to parse node: {node}! Unsupported type: {type(node)}. Allowed types: {Union[LeafType, NodeType]}")
    return ret

def tree_put(node: NodeType | LeafType, key: str, swaps: List[List[Any]], curdepth=1) -> NodeType | LeafType:
    ret = deepcopy(node)
    
    if curdepth > MAX_RECURSION_DEPTH:
        raise RecursionError

    if isinstance(node, LeafType):
        return ret
    elif isinstance(node, list):
        for i, entry in enumerate(node):
            ret[i] = tree_put(entry, key=key, swaps=swaps, curdepth=curdepth + 1)
    elif isinstance(node, dict):
        """
            We have to separate deletion, updates and recursive calls to tree_put.
        """
        keys_to_delete = []
        updates = {}

        for k, v in node.items():
            if k == key:
                keys_to_delete.append(k)
                updates.update(swaps.pop(0))
            else:
                ret[k] = tree_put(v, key=key, swaps=swaps, curdepth=curdepth + 1)

        # Remove keys marked for deletion
        for k in keys_to_delete:
            del ret[k]

        # Apply updates safely
        ret = recursive_update(ret, updates, curdepth=1)

    else:
        raise TypeError(f"Encountered Error while trying to parse node: {node}! Unsupported type: {type(node)}. Allowed types: {Union[LeafType, NodeType]}")

    return ret

def tree_remove(node : NodeType | LeafType, remove_key: str) -> NodeType | LeafType:
    """
        Removes every leaf of type key : value where key == `key`.
    """
    ret = deepcopy(node)
    if isinstance(node, dict):
        for key, value in node.items():
            if key.startswith(remove_key):
                del ret[key]
            else:
                ret[key] = tree_remove(value, remove_key=remove_key)
    if isinstance(node, list):
        ret = [tree_remove(value, remove_key=remove_key) for value in node]
        
    return ret
