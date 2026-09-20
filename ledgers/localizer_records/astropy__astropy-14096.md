# Instance: `astropy__astropy-14096`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
Subclassed SkyCoord gives misleading attribute access message
I'm trying to subclass `SkyCoord`, and add some custom properties. This all seems to be working fine, but when I have a custom property (`prop` below) that tries to access a non-existent attribute (`random_attr`) below, the error message is misleading because it says `prop` doesn't exist, where it should say `random_attr` doesn't exist.

```python
import astropy.coordinates as coord


class custom_coord(coord.SkyCoord):
    @property
    def prop(self):
        return self.random_attr


c = custom_coord('00h42m30s', '+41d12m00s', frame='icrs')
c.prop
```

raises
```
Traceback (most recent call last):
  File "test.py", line 11, in <module>
    c.prop
  File "/Users/dstansby/miniconda3/lib/python3.7/site-packages/astropy/coordinates/sky_coordinate.py", line 600, in __getattr__
    .format(self.__class__.__name__, attr))
AttributeError: 'custom_coord' object has no attribute 'prop'
```
```

## Stage 3 — Symptoms extracted

- exception types: `['AttributeError']`
- error messages: `["'custom_coord' object has no attribute 'prop'"]`
- behaviors: `['misleading attribute error message', 'incorrect attribute lookup']`
- named APIs: `['astropy.coordinates.SkyCoord', 'SkyCoord.__getattr__']`
- stack frames: `[{'file': 'test.py', 'func': '<module>', 'line': 11}, {'file': '/Users/dstansby/miniconda3/lib/python3.7/site-packages/astropy/coordinates/sky_coordinate.py', 'func': '__getattr__', 'line': 600}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `astropy/coordinates/sky_coordinate.py` | Handles attribute access and might be the source of the misleading error message. |
| 2 | `astropy/coordinates/baseframe.py` | Defines the base class for coordinate frames and attribute access. |
| 3 | `astropy/coordinates/__init__.py` | Top-level file for the coordinates subpackage, may need changes to expose new functionality. |
| 4 | `astropy/coordinates/attributes.py` | Defines the Attribute descriptors used in coordinate frames. |
| 5 | `astropy/coordinates/tests/test_frames.py` | Tests for coordinate frames, including attribute access. |
| 6 | `astropy/coordinates/tests/test_sky_coord.py` | Tests for SkyCoord, including attribute access. |
| 7 | `astropy/coordinates/angles.py` | Deals with angle representations, which might be relevant to attribute access. |
| 8 | `astropy/coordinates/representation.py` | Defines how coordinate data is represented, which is relevant to attribute access. |
| 9 | `astropy/coordinates/errors.py` | Defines custom exception classes for coordinates, including those related to attribute errors. |
| 10 | `astropy/coordinates/tests/test_angles.py` | Tests for the Angle class, which is a fundamental component of SkyCoord. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 0, rejected: 2

**Per-candidate deliberation traces**

#### ✓ LEADING — `astropy/coordinates/sky_coordinate.py::SkyCoord.__getattr__`

- **Q1 Role.** This function overrides `getattr` to dynamically provide attributes on `SkyCoord` objects, primarily for coordinate frame transformations and accessing frame-specific attributes.
- **Q2 Connection to symptom.** Yes, this function is the direct source of the misleading error message. The execution path is: 
1. The user code `c.prop` invokes the property getter on the `custom_coord` subclass.
2. The getter attempts to access `self.random_attr`, which does not exist.
3. This triggers a call to `SkyCoord.__getattr__(self, 'random_attr')`.
4. This `__getattr__` call correctly fails to find 'random_attr' and raises an `AttributeError`.
5. Due to a subtle behavior in Python's descriptor and attribute access protocol, the `AttributeError` raised from within the property getter is caught by the `object.__getattribute__` machinery.
6. `object.__getattribute__` then incorrectly assumes the original attribute access for 'prop' failed, and as a fallback, it calls `__getattr__` again, but this time with `attr='prop'`.
7. `SkyCoord.__getattr__` is now executed with `attr='prop'`, which it cannot resolve through its dynamic lookups.
8. It falls through to the final `raise` statement, issuing the misleading error `'custom_coord' object has no attribute 'prop'`.
- **Q3 Counterfactual.** `yes` — Modifying this function to detect when it's called for an attribute that already exists on the class (like a property) would allow it to raise a more informative error message, thus eliminating the symptom.
- **Q4 Alternatives considered.**
  - `object.__getattribute__` — This is the ultimate source of the confusing behavior, but it's part of the Python C implementation and cannot be changed.
  - `custom_coord.prop` — The user could add a try/except block here, but that would be a workaround, not a fix for the misleading error from the library.
  - `astropy.coordinates.baseframe.BaseCoordinateFrame.__getattr__` — This is involved in attribute resolution on frame objects but is not the source of the final, misleading error message.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function raises the misleading error due to a known Python quirk, and modifying it is the correct way to fix the symptom.

#### ✗ REJECTED — `astropy/visualization/wcsaxes/core.py::WCSAxes.plot_coord`

- **Q1 Role.** This is a method on the `WCSAxes` class used for plotting `SkyCoord` or `BaseCoordinateFrame` objects onto a map projection.
- **Q2 Connection to symptom.** No path exists. The user's code snippet for reproducing the bug involves only the definition and attribute access of a `SkyCoord` subclass; it does not perform any plotting or use the `wcsaxes` module.
- **Q3 Counterfactual.** `no` — Since this function is never called in the execution path that leads to the symptom, modifying it would have no effect on the outcome.
- **Q4 Alternatives considered.**
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__getattr__` — This function is in the traceback and is the source of the error message, making it the prime suspect.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is related to plotting and is completely unrelated to the attribute access error shown in the traceback.

#### ✗ REJECTED — `astropy/visualization/wcsaxes/core.py::WCSAxes.scatter_coord`

- **Q1 Role.** This is a method on the `WCSAxes` class used for creating scatter plots of `SkyCoord` or `BaseCoordinateFrame` objects onto a map projection.
- **Q2 Connection to symptom.** No path exists. The user's code snippet for reproducing the bug involves only the definition and attribute access of a `SkyCoord` subclass; it does not perform any plotting or use the `wcsaxes` module.
- **Q3 Counterfactual.** `no` — Since this function is never called in the execution path that leads to the symptom, modifying it would have no effect on the outcome.
- **Q4 Alternatives considered.**
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__getattr__` — This function is in the traceback and is the source of the error message, making it the prime suspect.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is related to plotting and is completely unrelated to the attribute access error shown in the traceback.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `astropy/coordinates/sky_coordinate.py::SkyCoord.__getattr__` | high | This function raises the misleading error due to a known Python quirk, and modifying it is the correct way to fix the symptom. | Before raising the final AttributeError, check if the attribute exists on the class (e.g., `hasattr(self.__class__, attr)`) and if so, raise a more specific err |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `astropy/visualization/wcsaxes/core.py::WCSAxes.plot_coord` | high | This function is related to plotting and is completely unrelated to the attribute access error shown in the traceback. |  |
| `astropy/visualization/wcsaxes/core.py::WCSAxes.scatter_coord` | high | This function is related to plotting and is completely unrelated to the attribute access error shown in the traceback. |  |

**Causal chains (per candidate)**

- `astropy/coordinates/sky_coordinate.py::SkyCoord.__getattr__`  (score=10.0)  \
  User code accesses `c.prop`, invoking the property getter. → The property getter `custom_coord.prop` attempts to access `self.random_attr`. → The access to `random_attr` fails, and Python calls `SkyCoord.__getattr__(self, 'random_attr')`. → `__getattr__` raises an `AttributeError` because it cannot resolve `random_attr`. → Python's `object.__getattribute__` catches this `AttributeError` raised from within the property. → It misinterprets this as a failure to find `prop` itself and calls `__getattr__(self, 'prop')` as a fallback.
- `astropy/visualization/wcsaxes/core.py::WCSAxes.plot_coord`  (score=0.0)  \
  
- `astropy/visualization/wcsaxes/core.py::WCSAxes.scatter_coord`  (score=0.0)  \
  

### Abductive step #2 (iteration=6)

- leading: 0, considering: 0, rejected: 3

**Per-candidate deliberation traces**

#### ✗ REJECTED — `astropy/coordinates/sky_coordinate.py::SkyCoord.__delattr__`

- **Q1 Role.** This function handles the deletion of attributes on a SkyCoord object, including proxying deletion to the underlying coordinate frame.
- **Q2 Connection to symptom.** No path exists. The observed symptom is an `AttributeError` during attribute access (getting an attribute), while this function is only called for attribute deletion (e.g., `del c.attribute`). The user's code does not use `del`.
- **Q3 Counterfactual.** `no` — Modifying the logic for attribute deletion would have no effect on the logic for attribute access, which is where the bug manifests.
- **Q4 Alternatives considered.**
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__getattr__` — Preferred, as it is explicitly in the stack trace and handles attribute access.
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__setattr__` — Considered as it's part of attribute handling, but the bug is on read, not write.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function handles attribute deletion, not access, and is not on the execution path of the bug.

#### ✗ REJECTED — `astropy/coordinates/solar_system.py::get_moon`

- **Q1 Role.** This is a high-level convenience function that computes and returns a `SkyCoord` object for the Earth's Moon at a specific time.
- **Q2 Connection to symptom.** No path exists. This function is a factory for creating `SkyCoord` instances. The user's code creates a `custom_coord` instance directly and does not call `get_moon`. The bug is in the behavior of the `SkyCoord` class, not its instantiation.
- **Q3 Counterfactual.** `no` — The function is not involved in the execution path of the bug, so modifying it would have no effect on the symptom.
- **Q4 Alternatives considered.**
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__init__` — A more relevant factory-like function, but the bug is in attribute access logic, not initialization.
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__getattr__` — Preferred, as it is directly implicated by the stack trace.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is a factory function that creates SkyCoord objects and is not called in the code that demonstrates the bug.

#### ✗ REJECTED — `astropy/wcs/utils.py::pixel_to_skycoord`

- **Q1 Role.** This function converts a set of pixel coordinates from a WCS object into a `SkyCoord` object.
- **Q2 Connection to symptom.** No path exists. Much like `get_moon`, this is a factory function that produces `SkyCoord` instances. The user's code does not use it, and the bug relates to attribute access on an already-created object.
- **Q3 Counterfactual.** `no` — This function is not on the execution path of the bug. Modifying it cannot fix the symptom.
- **Q4 Alternatives considered.**
  - `astropy.coordinates.SkyCoord.from_pixel` — A similar factory method on the class itself, but still irrelevant to the attribute access mechanism.
  - `astropy.coordinates.sky_coordinate.py::SkyCoord.__getattr__` — Preferred, as the stack trace shows it is the source of the misleading error message.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This is another factory function for SkyCoord and is not involved in the attribute access mechanism that causes the bug.

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `astropy/coordinates/sky_coordinate.py::SkyCoord.__delattr__` | high | This function handles attribute deletion, not access, and is not on the execution path of the bug. |  |
| `astropy/coordinates/solar_system.py::get_moon` | high | This is a factory function that creates SkyCoord objects and is not called in the code that demonstrates the bug. |  |
| `astropy/wcs/utils.py::pixel_to_skycoord` | high | This is another factory function for SkyCoord and is not involved in the attribute access mechanism that causes the bug. |  |

**Causal chains (per candidate)**

- `astropy/coordinates/sky_coordinate.py::SkyCoord.__delattr__`  (score=0.0)  \
  
- `astropy/coordinates/solar_system.py::get_moon`  (score=0.0)  \
  
- `astropy/wcs/utils.py::pixel_to_skycoord`  (score=0.0)  \
  

**next_to_explore:** `['astropy.coordinates.sky_coordinate.py::SkyCoord.__getattr__']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__getattr__` | 1.0 |
| 2 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__delattr__` | 0.0 |
| 3 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__setattr__` | 0.0 |
| 4 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__init__` | 0.0 |
| 5 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__repr__` | 0.0 |
| 6 | `astropy/wcs/utils.py::pixel_to_skycoord` | 0.0 |
| 7 | `astropy/visualization/wcsaxes/core.py::WCSAxes.plot_coord` | 0.0 |
| 8 | `astropy/coordinates/baseframe.py::BaseCoordinateFrame._frame_attrs_repr` | 0.0 |
| 9 | `astropy/visualization/wcsaxes/core.py::WCSAxes.scatter_coord` | 0.0 |
| 10 | `astropy/coordinates/baseframe.py::BaseCoordinateFrame._replicate` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__getattr__` | 1.000 | high | 1/1 | (869, 900) |
| 2 | `astropy/coordinates/baseframe.py::BaseCoordinateFrame.__init_subclass__` | 0.273 | high | 1/1 | (225, 304) |
| 3 | `astropy/coordinates/attributes.py::CoordinateAttribute.convert_input` | 0.262 | high | 1/1 | (441, 473) |
| 4 | `astropy/coordinates/solar_system.py::get_moon` | 0.260 | high | 1/1 | (503, 535) |
| 5 | `astropy/coordinates/attributes.py::Attribute.__get__` | 0.259 | high | 1/1 | (100, 136) |
| 6 | `astropy/coordinates/attributes.py::CoordinateAttribute.__init__` | 0.255 | high | 1/1 | (437, 439) |
| 7 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__delattr__` | 0.000 | high | 1/1 | (929, 952) |
| 8 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__setattr__` | 0.000 | high | 1/1 | (902, 927) |
| 9 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__init__` | 0.000 | high | 1/1 | (293, 361) |
| 10 | `astropy/coordinates/sky_coordinate.py::SkyCoord.__repr__` | 0.000 | high | 1/1 | (978, 989) |
