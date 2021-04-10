# mc2obj
Simple python module that converts any minecraft block in a resource pack to a OBJ/MTL pair.

Import `mc2obj.py`, and call `convert("resource pack path", "your block name")` to use it.
Example:
```python
from mc2obj import convert

convert("./minecraft", "minecraft:redstone_torch[lit=false]", output_path="out/")
```
