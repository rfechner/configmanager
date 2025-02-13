## Simple Hackable Configmanager

> [!IMPORTANT] 
> This is a small hackable configuration manager. It *just* does what you expect it to do. Load > from yaml, importing, string interpolation, expanding axes, manual overwrite, yield mutable
> /immutable dictionaries whose keys you may access by attributes.

### Basic Usage

```python
from configmanager import load_config, ImmutableAttributDict, AttributeDict

# may return multiple configs, if axes are expanded
configs : List[AttributeDict] = load_config('tests/model.yaml', make_immutable=False)

# make immutable
immutable_config = configs[0]._immutable_copy()

# make mutable again
mutable_config = immutable_config._mutable_copy()

# hashable (for use in jax.jitted regions)
hash(mutable_config)
```
#### Features - Imports

```yaml
# config/mymodel/kwargs1.yaml
param1 : 1
param2 : "heythere buddy!"
```

```yaml
# config/model.yaml
model:
    kwargs:
        __import__: "configs/mymodel/kwargs1.yaml"
```

... resolves to ...

```yaml
model:
    kwargs:
        param1 : 1
        param2 : "heythere buddy!"
```

> [!NOTE] 
> Per default, all nested dictionaries are merged instead of overwritten. In case you want to specify custom overwrite behaviour, please take a look further down below.

#### Features - Grids 

> [!NOTE] 
> A really nice addition is the use of `expandable axes`. This lets you specify a (nested) grid of axes in a single .yaml file.

```yaml
model:
    kwargs:
        __axis__:
            - batchnorm: false
                use_bottleneck: false
            - batchnorm: true
                use_bottleneck: false
                additional_param: 42
            - {} # defaults

optim:    
    kwargs:
        __axis__:
            - path: 'optax.adamw'
            - path: 'your.module.optimizer'
```

Turned into a bunch of configurations:

```python
"""
    this will return a list of 3 * 2 configs, as we have two
    axes which are expanded. Axis one `model.kwargs` has three entries,
    axis `optim.kwargs` has 2 entries. 
"""
configs = load_config('tests/model.yaml')
```

#### Features - String interpolation

```yaml
data:
    shape: [42, 1]

model:
    kwargs:
        input_shape : "$(data.shape)" # resolves to [42, 1]
```

#### Custom Overwrites

Sometimes, you wouldn't want dictionaries to be merged. If you're instead looking for a hard-overwrite option, here it is:

```yaml
__import__: "some_default_setup.yaml"

optim:
    path: "my.module.optim"
    __overwrite__(kwargs):
        please_just_keep : "this keyword argument, instead of merging"
```

Instead of importing a default optimizer which would probably have the key `kwargs` defined, we overwrite. This resolves to something like:

```yaml
model:
    ...

...

optim:
    path: "my.module.optim"
    kwargs:
        please_just_keep : "this keyword argument, instead of merging"

```
