from typing import *
from ._load import load
from ._structs import *
from ._config import *
from ._eval import extract

from copy import deepcopy


def recursive_update(current : dict, update : dict, curdepth : int, overwrite : bool = False) -> dict:
    if curdepth > MAX_RECURSION_DEPTH:
        raise RecursionError

    ret = deepcopy(current)
    if not isinstance(current, dict):
        return ret

    for key, value in update.items():
        if not overwrite and \
            key in ret and \
            (isinstance(ret[key], dict) and isinstance(value, dict)):
            ret[key] = recursive_update(ret[key], value, curdepth=curdepth + 1, overwrite=overwrite)
        else:
            ret[key] = value
    return ret

def contains_key(node : NodeType | LeafType, key : str) -> bool:
    if isinstance(node, LeafType):
        return False
    elif isinstance(node, list):
        return any(contains_key(subnode, key=key) for subnode in node)
    elif isinstance(node, dict):
        if key in node:
            return True
        return any(contains_key(v, key=key) for v in node.values())
    else:
        raise TypeError(f"Encountered Error while trying to parse value: {node} of type {type(node)}. Allowed types: {Union[LeafType, NodeType]}")

def parse(current : NodeType | LeafType, curdepth : int, overwrite : bool = False) -> Any:
    config = recursive_parse(current, curdepth, overwrite)
    config = tree_remove(config, remove_key=IMPORT_KEY)
    config = tree_remove(config, remove_key=OVERWRITE_KEY)
    return config

def recursive_parse(current : NodeType | LeafType, curdepth : int, overwrite : bool = False) -> Any:
    if curdepth > MAX_RECURSION_DEPTH:
        raise RecursionError("Maximum recursion depth reached! Might have circular import!")

    ret = deepcopy(current)
    if isinstance(current, LeafType):
        pass
    elif isinstance(current, list):
        ret = [recursive_parse(v, curdepth=curdepth + 1, overwrite=overwrite) for v in current]
    elif isinstance(current, dict):
        for key, value in current.items():
            ckey = key
            match = extract(key, OVERWRITE_PATTERN)
            local_overwrite = overwrite or (match is not None)
            key = match if match else key

            if match == IMPORT_KEY:
                raise ValueError("overwriting an import statement isn't supported.")

            if key == IMPORT_KEY:
                if isinstance(value, str):
                    value = [value]
                if not isinstance(value, list):
                    raise ValueError("Import Statements can only be a list of strings or a single string!")
                del ret[key]
                for importstmt in value:
                    update = recursive_parse(load(importstmt), curdepth=curdepth + 1, overwrite=local_overwrite)
                    ret = recursive_update(ret, update, curdepth=1, overwrite=local_overwrite)
            else:
                if match:
                    del ret[ckey]
                update = {key: recursive_parse(value, curdepth=curdepth + 1, overwrite=local_overwrite)}
                ret = recursive_update(ret, update, curdepth=1, overwrite=local_overwrite)
    else:
        raise TypeError(f"Encountered Error while trying to parse value: {value} of type {type(value)}. Allowed types: {Union[LeafType, NodeType]}")
    return ret

def tree_get(node : NodeType | LeafType, key : str) -> List[List[Any]]:
    ret = []
    if isinstance(node, LeafType):
        pass
    elif isinstance(node, list):
        for entry in node:
            ret.extend(tree_get(entry, key=key))
    elif isinstance(node, dict):
        for k, v in node.items():
            if k == AXIS_KEY:
                ret.append(v)
            else:
                ret.extend(tree_get(v, key=key))
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
        keys_to_delete = []
        updates = {}

        for k, v in node.items():
            if k == key:
                keys_to_delete.append(k)
                updates.update(swaps.pop(0))
            else:
                ret[k] = tree_put(v, key=key, swaps=swaps, curdepth=curdepth + 1)

        for k in keys_to_delete:
            del ret[k]

        ret = recursive_update(ret, updates, curdepth=1)
    else:
        raise TypeError(f"Encountered Error while trying to parse node: {node}! Unsupported type: {type(node)}. Allowed types: {Union[LeafType, NodeType]}")

    return ret

def tree_remove(node : NodeType | LeafType, remove_key: str) -> NodeType | LeafType:
    if isinstance(node, dict):
        return {k: tree_remove(v, remove_key) for k, v in node.items()
                if not k.startswith(remove_key)}
    if isinstance(node, list):
        return [tree_remove(v, remove_key) for v in node]
    return node
