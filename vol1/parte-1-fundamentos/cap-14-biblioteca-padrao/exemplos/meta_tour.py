"""importlib.metadata e importlib.resources."""
import importlib
import importlib.metadata as md
import importlib.resources as res
import importlib.util

print(md.version("pytest").count(".") >= 1)
print(sorted(d.metadata["Name"] for d in md.distributions())[:3])
print(res.files("json").joinpath("tool.py").read_text()[:12].strip())
mod = importlib.import_module("json.tool")
print(mod.__name__)
print(importlib.util.find_spec("json").origin.endswith("__init__.py"))
