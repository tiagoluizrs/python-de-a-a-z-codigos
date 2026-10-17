"""Gabarito do exercício 1."""
import re

NAME = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
VERSION = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$")
CLAUSE = re.compile(r"^\s*(~=|==|!=|<=|>=|<|>)\s*\d+(\.\d+)*\s*$")
SCRIPT = re.compile(r"^[\w.]+:[\w.]+$")


def validate_project(project, files_exist=lambda path: True):
    problems = set()
    name = project.get("name")
    if not name:
        problems.add("no-name")
    elif not NAME.match(name):
        problems.add("bad-name")
    version = project.get("version")
    if version is None:
        if "version" not in project.get("dynamic", []):
            problems.add("no-version")
    elif not VERSION.match(str(version)):
        problems.add("bad-version")
    requires = project.get("requires-python")
    if not requires:
        problems.add("no-requires-python")
    elif not all(CLAUSE.match(part) for part in requires.split(",")):
        problems.add("bad-requires-python")
    if not project.get("description"):
        problems.add("no-description")
    readme = project.get("readme")
    if readme is None:
        problems.add("no-readme")
    else:
        path = readme["file"] if isinstance(readme, dict) else readme
        if not files_exist(path):
            problems.add("missing-readme-file")
    if "license" not in project and "license-files" not in project:
        problems.add("no-license")
    if isinstance(project.get("license"), dict):
        problems.add("license-table")
    if any(not SCRIPT.match(target) for target in project.get("scripts", {}).values()):
        problems.add("bad-script")
    return sorted(problems)
