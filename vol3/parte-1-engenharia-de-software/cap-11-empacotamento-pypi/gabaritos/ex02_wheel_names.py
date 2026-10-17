"""Gabarito do exercício 2."""
import itertools


def parse_wheel_filename(filename):
    if not filename.endswith(".whl"):
        raise ValueError("não é uma wheel")
    parts = filename[:-4].split("-")
    if len(parts) == 5:
        name, version, python, abi, platform = parts
        build = None
    elif len(parts) == 6 and parts[2][:1].isdigit():
        name, version, build, python, abi, platform = parts
    else:
        raise ValueError(f"nome de wheel inválido: {filename!r}")
    return {"name": name, "version": version, "build": build, "python": python.split("."), "abi": abi.split("."),
            "platform": platform.split(".")}


def expand_tags(info):
    return {"-".join(t) for t in itertools.product(info["python"], info["abi"], info["platform"])}


def best_wheel(filenames, supported):
    rank = {tag: index for index, tag in enumerate(supported)}
    best, best_key = None, None
    for filename in filenames:
        try:
            info = parse_wheel_filename(filename)
        except ValueError:
            continue
        indexes = [rank[tag] for tag in expand_tags(info) if tag in rank]
        if not indexes:
            continue
        version = tuple(int(x) for x in info["version"].split(".") if x.isdigit())
        key = (min(indexes), tuple(-v for v in version))
        if best_key is None or key < best_key:
            best, best_key = filename, key
    return best
