import subprocess
import sys
import zipfile

import pytest


# ---------- 1: validate_project ----------
GOOD = {"name": "my-pkg", "version": "1.2.3", "description": "d", "readme": "README.md", "requires-python": ">=3.10,<4",
        "license": "MIT", "scripts": {"cmd": "my_pkg.cli:main"}}


def test_validate_good_project(load_exercise):
    validate = load_exercise("ex01_metadata").validate_project
    assert validate(GOOD) == []
    assert validate({**GOOD, "readme": {"file": "README.rst", "content-type": "text/x-rst"}}) == []
    dynamic = {k: v for k, v in GOOD.items() if k != "version"} | {"dynamic": ["version"]}
    assert validate(dynamic) == []
    assert validate({k: v for k, v in GOOD.items() if k != "license"} | {"license-files": ["LICENSE"]}) == []


@pytest.mark.parametrize("change, expected", [
    ({"name": None}, ["no-name"]), ({"name": "-bad"}, ["bad-name"]), ({"name": "has space"}, ["bad-name"]),
    ({"version": None}, ["no-version"]), ({"version": "1.x"}, ["bad-version"]), ({"version": "v1.0"}, ["bad-version"]),
    ({"version": "2.0.0rc1"}, []), ({"version": "1.0.post2.dev1"}, []),
    ({"requires-python": None}, ["no-requires-python"]), ({"requires-python": "3.10"}, ["bad-requires-python"]),
    ({"requires-python": ">=3.10, !=3.11"}, []), ({"requires-python": ">=3.10;<4"}, ["bad-requires-python"]),
    ({"description": None}, ["no-description"]), ({"readme": None}, ["no-readme"]),
    ({"license": None}, ["no-license"]), ({"license": {"text": "MIT"}}, ["license-table"]),
    ({"scripts": {"cmd": "no_colon"}}, ["bad-script"]), ({"scripts": {"a": "pkg.mod:func", "b": "x"}}, ["bad-script"]),
])
def test_validate_single_problems(load_exercise, change, expected):
    project = {**GOOD, **change}
    project = {k: v for k, v in project.items() if v is not None}
    assert load_exercise("ex01_metadata").validate_project(project) == expected


def test_validate_missing_readme_file_and_many(load_exercise):
    validate = load_exercise("ex01_metadata").validate_project
    assert validate(GOOD, files_exist=lambda p: p != "README.md") == ["missing-readme-file"]
    assert validate({}) == ["no-description", "no-license", "no-name", "no-readme", "no-requires-python", "no-version"]


# ---------- 2: wheel names ----------
def test_parse_wheel_filename(load_exercise):
    parse = load_exercise("ex02_wheel_names").parse_wheel_filename
    assert parse("six-1.17.0-py2.py3-none-any.whl") == {"name": "six", "version": "1.17.0", "build": None, "python": ["py2", "py3"],
                                                        "abi": ["none"], "platform": ["any"]}
    info = parse("numpy-2.4.0-1-cp315-cp315-win_amd64.whl")
    assert info["build"] == "1" and info["python"] == ["cp315"] and info["platform"] == ["win_amd64"]
    for bad in ("six-1.17.0.tar.gz", "six-1.0.whl", "a-b-c-d-e-f-g.whl", "a-1.0-py3-none-any-extra.whl"):
        with pytest.raises(ValueError):
            parse(bad)


def test_expand_tags(load_exercise):
    m = load_exercise("ex02_wheel_names")
    assert m.expand_tags(m.parse_wheel_filename("six-1.17.0-py2.py3-none-any.whl")) == {"py2-none-any", "py3-none-any"}
    assert m.expand_tags(m.parse_wheel_filename("x-1-cp311-abi3.cp311-win_amd64.manylinux_2_17_x86_64.whl")) == {
        "cp311-abi3-win_amd64", "cp311-abi3-manylinux_2_17_x86_64", "cp311-cp311-win_amd64", "cp311-cp311-manylinux_2_17_x86_64"}


def test_best_wheel(load_exercise):
    best = load_exercise("ex02_wheel_names").best_wheel
    supported = ["cp315-cp315-win_amd64", "cp315-abi3-win_amd64", "cp314-abi3-win_amd64", "py3-none-win_amd64", "py3-none-any"]
    files = ["pkg-1.0-py3-none-any.whl", "pkg-1.0-cp315-cp315-win_amd64.whl", "pkg-1.0-cp312-cp312-win_amd64.whl", "pkg-1.0.tar.gz"]
    assert best(files, supported) == "pkg-1.0-cp315-cp315-win_amd64.whl"
    assert best([f for f in files if "cp315" not in f], supported) == "pkg-1.0-py3-none-any.whl"
    assert best(["pkg-1.0-cp312-cp312-win_amd64.whl", "x.txt"], supported) is None and best([], supported) is None
    tie = ["pkg-1.9.0-py3-none-any.whl", "pkg-1.10.0-py3-none-any.whl", "pkg-1.2.0-py3-none-any.whl"]
    assert best(tie, supported) == "pkg-1.10.0-py3-none-any.whl"
    assert best(["a-1-py2.py3-none-any.whl"], supported) == "a-1-py2.py3-none-any.whl"


# ---------- 3: sdist ----------
def make_tree(root):
    for relative in ("src/pkg/__init__.py", "src/pkg/mod.py", "src/pkg/__pycache__/mod.cpython-315.pyc", "tests/test_a.py", "docs/index.md",
                     "README.md", "LICENSE", "dist/old.whl", ".git/config", ".venv/lib/x.py", "build/lib/y.py", "notes.log", "src/pkg/stale.pyc"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")


def test_collect_files_defaults(load_exercise, tmp_path):
    collect = load_exercise("ex03_sdist_files").collect_files
    make_tree(tmp_path)
    assert collect(tmp_path) == ["LICENSE", "README.md", "docs/index.md", "notes.log", "src/pkg/__init__.py", "src/pkg/mod.py", "tests/test_a.py"]


def test_collect_files_include_exclude(load_exercise, tmp_path):
    collect = load_exercise("ex03_sdist_files").collect_files
    make_tree(tmp_path)
    assert collect(tmp_path, include=("src/**/*", "README.md", "LICENSE")) == ["LICENSE", "README.md", "src/pkg/__init__.py", "src/pkg/mod.py"]
    assert collect(tmp_path, exclude=("tests/*", "*.log", "docs/*")) == ["LICENSE", "README.md", "src/pkg/__init__.py", "src/pkg/mod.py"]
    assert collect(tmp_path, include=("nada/*",)) == []


# ---------- 4: RECORD ----------
def test_record_line_and_make_record(load_exercise):
    m = load_exercise("ex04_record")
    assert m.record_line("a/b.py", b"hello") == "a/b.py,sha256=LPJNul-wow4m6DsqxbninhsWHlwfp0JecwQzYpOLmCQ,5"
    record = m.make_record({"z.py": b"1", "a.py": b"22"}, "x-1.dist-info/RECORD")
    lines = record.splitlines()
    assert [l.split(",")[0] for l in lines] == ["a.py", "z.py", "x-1.dist-info/RECORD"] and lines[-1] == "x-1.dist-info/RECORD,," and record.endswith("\n")
    assert lines[0].endswith(",2") and "=" not in lines[0].split(",")[1][len("sha256="):]


def make_wheel(path, files, record=None, extra=None):
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
        if record is not None:
            archive.writestr("x-1.dist-info/RECORD", record)
        for name, data in (extra or {}).items():
            archive.writestr(name, data)


def test_verify_wheel(load_exercise, tmp_path):
    m = load_exercise("ex04_record")
    files = {"pkg/__init__.py": b"print(1)\n", "x-1.dist-info/METADATA": b"Name: x\n"}
    good = tmp_path / "good.whl"
    make_wheel(good, files, record=m.make_record(files, "x-1.dist-info/RECORD"))
    assert m.verify_wheel(good) == []
    tampered = tmp_path / "t.whl"
    make_wheel(tampered, {**files, "pkg/__init__.py": b"print(2)\n"}, record=m.make_record(files, "x-1.dist-info/RECORD"))
    assert m.verify_wheel(tampered) == ["hash:pkg/__init__.py"]
    missing = tmp_path / "m.whl"
    make_wheel(missing, {"x-1.dist-info/METADATA": b"Name: x\n"}, record=m.make_record(files, "x-1.dist-info/RECORD"))
    assert m.verify_wheel(missing) == ["missing:pkg/__init__.py"]
    extra = tmp_path / "e.whl"
    make_wheel(extra, files, record=m.make_record(files, "x-1.dist-info/RECORD"), extra={"pkg/evil.py": b"x"})
    assert m.verify_wheel(extra) == ["extra:pkg/evil.py"]
    none = tmp_path / "n.whl"
    make_wheel(none, files)
    with pytest.raises(ValueError):
        m.verify_wheel(none)


# ---------- 5: build_wheel ----------
def test_build_wheel_structure(load_exercise, tmp_path):
    build = load_exercise("ex05_build_wheel").build_wheel
    wheel = build(tmp_path, "my-pkg", "0.1.0", {"my_pkg/__init__.py": "VALUE = 41\n", "my_pkg/cli.py": "def main():\n    print('oi')\n"},
                  entry_points={"console_scripts": {"mycmd": "my_pkg.cli:main"}}, requires=["requests>=2", "rich"], requires_python=">=3.10")
    assert wheel.name == "my_pkg-0.1.0-py3-none-any.whl" and wheel.parent == tmp_path
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        assert {"my_pkg/__init__.py", "my_pkg/cli.py", "my_pkg-0.1.0.dist-info/METADATA", "my_pkg-0.1.0.dist-info/WHEEL",
                "my_pkg-0.1.0.dist-info/entry_points.txt", "my_pkg-0.1.0.dist-info/RECORD"} <= names
        metadata = archive.read("my_pkg-0.1.0.dist-info/METADATA").decode()
        assert "Name: my-pkg" in metadata and "Version: 0.1.0" in metadata and "Requires-Python: >=3.10" in metadata
        assert metadata.count("Requires-Dist:") == 2 and "Requires-Dist: requests>=2" in metadata
        assert "Tag: py3-none-any" in archive.read("my_pkg-0.1.0.dist-info/WHEEL").decode()
        assert "[console_scripts]" in archive.read("my_pkg-0.1.0.dist-info/entry_points.txt").decode()


def test_build_wheel_record_is_valid(load_exercise, tmp_path):
    build = load_exercise("ex05_build_wheel").build_wheel
    wheel = build(tmp_path, "pkg", "2.0", {"pkg/__init__.py": "x = 1\n"})
    import base64
    import hashlib
    with zipfile.ZipFile(wheel) as archive:
        record = archive.read("pkg-2.0.dist-info/RECORD").decode().splitlines()
        assert record[-1] == "pkg-2.0.dist-info/RECORD,,"
        listed = {line.rsplit(",", 2)[0] for line in record}
        assert listed == set(archive.namelist())
        for line in record[:-1]:
            path, digest, size = line.rsplit(",", 2)
            data = archive.read(path)
            expected = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
            assert digest == f"sha256={expected}" and int(size) == len(data)
        assert not archive.read("pkg-2.0.dist-info/METADATA").endswith(b"\n\n")


def test_build_wheel_is_importable_with_metadata(load_exercise, tmp_path):
    build = load_exercise("ex05_build_wheel").build_wheel
    wheel = build(tmp_path, "zippy-demo", "3.1.4", {"zippy_demo/__init__.py": "ANSWER = 42\n", "zippy_demo/cli.py": "def main():\n    return 'ok'\n"},
                  entry_points={"console_scripts": {"zippy": "zippy_demo.cli:main"}})
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import zippy_demo, importlib.metadata as m; d = m.distribution('zippy-demo'); "
            "print(zippy_demo.ANSWER, d.version, [e.value for e in d.entry_points])")
    result = subprocess.run([sys.executable, "-c", code, str(wheel)], capture_output=True, text=True)
    assert result.stdout.strip() == "42 3.1.4 ['zippy_demo.cli:main']", result.stderr


# ---------- 6: versions ----------
def test_bump(load_exercise):
    bump = load_exercise("ex06_release_version").bump
    assert bump("1.4.2", "minor") == "1.5.0" and bump("1.4.2", "major") == "2.0.0" and bump("1.4.2", "patch") == "1.4.3"
    assert bump("0.0.9", "patch") == "0.0.10" and bump("9.9.9", "major") == "10.0.0"
    for bad in ("1.4", "1.4.2rc1", "1.4.2.post1", "1.4.2.dev0", "v1.4.2", ""):
        with pytest.raises(ValueError):
            bump(bad, "minor")
    with pytest.raises(ValueError):
        bump("1.0.0", "huge")


def test_prerelease_flow(load_exercise):
    m = load_exercise("ex06_release_version")
    assert m.to_prerelease("1.5.0", "rc") == "1.5.0rc1" and m.to_prerelease("1.5.0rc1", "rc") == "1.5.0rc2"
    assert m.to_prerelease("1.5.0a3", "b") == "1.5.0b1" and m.to_prerelease("1.5.0b2", "rc") == "1.5.0rc1" and m.to_prerelease("1.5.0a1", "a") == "1.5.0a2"
    for version, kind in (("1.5.0rc1", "a"), ("1.5.0b1", "a"), ("1.5", "rc"), ("1.5.0", "x"), ("1.5.0.dev1", "rc")):
        with pytest.raises(ValueError):
            m.to_prerelease(version, kind)
    assert m.finalize("1.5.0rc2") == "1.5.0" and m.finalize("1.5.0") == "1.5.0" and m.finalize("0.1.0a1") == "0.1.0"
    with pytest.raises(ValueError):
        m.finalize("1.5")
