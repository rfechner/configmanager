from typing import *

LeafType = Union[str, int, float, bool, None]
NodeType = Union[dict, list]

import json
import yaml
from copy import deepcopy
from typing import Hashable

class BaseDict(dict, Hashable):
    """
        Base class for all dictionaries. Includes yaml dump to string,
        asdict and a hash function.
    """
    def yaml_dump(self) -> str:
        """
            dumping with yaml will add tags to re-load the python class when re-loading.
            I dont want this, hence i first transform to a standart python dictionary, before
            dumping to yaml.
        """
        return yaml.dump(self.asdict(), indent=2, sort_keys=True)
    
    def asdict(self):
        d = {}

        for k, v in self.items():
            if isinstance(v, BaseDict):
                d[k] = v.asdict()
            else:
                d[k] = v
        return d
    
    def __repr__(self):
        return json.dumps(self, indent=4, sort_keys=True)
    
    def __hash__(self):
        return hash(self.__repr__())
    
    def get(self, key, default=None):
        """
            For whatever arcane reason

            ```python
            return super().get(key, default)
            ```

            just returns None if they key isn't found and not the specified default...
        """
        result = super().get(key)
        if not result:
            result = default
        return result


class AttributeDict(BaseDict):
    """A dict which allows attribute access to its keys."""

    def __getattr__(self, *args, **kwargs):
        try:
            return self.__getitem__(*args, **kwargs)
        except KeyError as e:
            raise AttributeError(e)
    
    def __deepcopy__(self, memo):
        return self.__class__(
            [(deepcopy(k, memo=memo), deepcopy(v, memo=memo)) for k, v in self.items()]
        )

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __delattr__(self, item):
        self.__delitem__(item)

    def _immutable_copy(self) -> "ImmutableAttributeDict":
        return recursive_objectify(self, make_immutable=True)


class ImmutableAttributeDict(AttributeDict):
    """
        An immutable dict which allows attribute access to its keys.
    """

    def __delattr__(self, item):
        raise TypeError("Setting object not mutable after settings are fixed!")

    def __delitem__(self, item):
        raise TypeError("Setting object not mutable after settings are fixed!")

    def __setattr__(self, key, value):
        raise TypeError("Setting object not mutable after settings are fixed!")

    def __setitem__(self, key, value):
        raise TypeError("Setting object not mutable after settings are fixed!")

    def __reduce__(self):
        # For overwriting dict pickling
        # https://stackoverflow.com/questions/21144845/how-can-i-unpickle-a-subclass-of-dict-that-validates-with-setitem-in-pytho
        return (AttributeDict, (self.__getstate__(),))

    def _mutable_copy(self):
        return recursive_objectify(self, make_immutable=False)

    def __getstate__(self):
        return self._mutable_copy()
    
def recursive_objectify(nested_dict, make_immutable=True):
    """
        Turns a nested_dict into a nested AttributeDict
    """
    result = deepcopy(nested_dict)
    
    for k, v in result.items():
        if isinstance(v, dict):
            result = dict(result)
            result[k] = recursive_objectify(v, make_immutable)
    
    if make_immutable:
        returned_result = ImmutableAttributeDict(result)
    else:
        returned_result = AttributeDict(result)
    
    return returned_result