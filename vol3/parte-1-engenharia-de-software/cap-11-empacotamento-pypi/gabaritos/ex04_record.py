"""Gabarito do exercício 4."""
import base64
import hashlib
import zipfile


def _digest(data):
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()


def record_line(path, data):
    return f"{path},sha256={_digest(data)},{len(data)}"


def make_record(files, record_path):
    lines = [record_line(path, files[path]) for path in sorted(files)]
    lines.append(f"{record_path},,")
    return "\n".join(lines) + "\n"


def verify_wheel(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        records = [n for n in names if n.endswith(".dist-info/RECORD")]
        if len(records) != 1:
            raise ValueError("RECORD ausente")
        record_name = records[0]
        listed = {}
        for line in archive.read(record_name).decode().splitlines():
            if line.strip():
                path, digest, size = line.rsplit(",", 2)
                listed[path] = (digest, size)
        problems = []
        for path, (digest, size) in listed.items():
            if path == record_name:
                continue
            if path not in names:
                problems.append(f"missing:{path}")
                continue
            data = archive.read(path)
            if digest != f"sha256={_digest(data)}" or size != str(len(data)):
                problems.append(f"hash:{path}")
        for name in names:
            if name != record_name and name not in listed:
                problems.append(f"extra:{name}")
        return sorted(problems)
