"""Gabarito do exercício 5."""
import base64
import hashlib
import re
import zipfile
from pathlib import Path


def _digest(data):
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()


def build_wheel(dest, name, version, files, entry_points=None, requires=(), requires_python=">=3.9"):
    norm = re.sub(r"[-.]+", "_", name)
    dist_info = f"{norm}-{version}.dist-info"
    contents = {path: text.encode("utf-8") for path, text in files.items()}
    metadata = ["Metadata-Version: 2.1", f"Name: {name}", f"Version: {version}", f"Requires-Python: {requires_python}"]
    metadata += [f"Requires-Dist: {item}" for item in requires]
    contents[f"{dist_info}/METADATA"] = ("\n".join(metadata) + "\n").encode()
    contents[f"{dist_info}/WHEEL"] = b"Wheel-Version: 1.0\nGenerator: manual\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    if entry_points:
        lines = []
        for group, commands in entry_points.items():
            lines.append(f"[{group}]")
            lines += [f"{cmd} = {target}" for cmd, target in commands.items()]
            lines.append("")
        contents[f"{dist_info}/entry_points.txt"] = ("\n".join(lines).rstrip("\n") + "\n").encode()
    record_path = f"{dist_info}/RECORD"
    record = [f"{path},sha256={_digest(data)},{len(data)}" for path, data in sorted(contents.items())]
    record.append(f"{record_path},,")
    contents[record_path] = ("\n".join(record) + "\n").encode()
    target = Path(dest) / f"{norm}-{version}-py3-none-any.whl"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, data in contents.items():
            archive.writestr(path, data)
    return target
