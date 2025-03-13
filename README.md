## Simple Hackable Configmanager

> [!IMPORTANT] 
> This is a small hackable configuration manager. It *just* does what you expect it to do. Load from json/yaml, [importing](#features---imports), [string interpolation](#features---string-interpolation), [expanding axes](#features---axes), [manual overwrite](#custom-overwrites), yield mutable
> /immutable dictionaries whose keys you may access by attributes.

### Basic Usage

```python
from your.utils import make_model, make_optim
from rox.configmanager import load_config, ImmutableAttributDict, AttributeDict

config : AttributeDict = load_config('tests/model.yaml', make_immutable=False)[0]

model = make_model(**conf.model.kwargs)
optimizer = make_optim(**conf.optim.kwargs)

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

#### Features - Axes 

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

seed: 0

optim:
    lr: 0.001
    info: "heytherebuddy"

model:
    kwargs:
        input_shape : "$(data.shape)" # resolves to [42, 1]
    checkpoint: "run-seed:$(seed)-lr:$(optim.lr)-checkpoint-.pickle" # resolves to "run-seed:0-lr:0.001-checkpoint.pickle"

$(optim.info) : $(optim.info) # resolves to "heytherebuddy" : "heytherebuddy"
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
