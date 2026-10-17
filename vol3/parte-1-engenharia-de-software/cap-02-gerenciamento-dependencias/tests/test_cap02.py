import pytest
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

VERSIONS = ["1.0.dev0", "1.0a1", "1.0a2", "1.0b1", "1.0rc1", "1.0", "1.0.post1.dev0", "1.0.post1",
            "1.0.1", "1.2", "1.10", "2.0.dev1", "2.0", "10.0"]


def test_version_key_orders_like_pep440(load_exercise):
    key = load_exercise("ex01_version").version_key
    assert sorted(reversed(VERSIONS), key=key) == VERSIONS
    assert sorted(reversed(VERSIONS), key=key) == sorted(VERSIONS, key=Version)
    assert key("1.0") == key("1.0.0") and key("1.0") < key("1.0.0.1")
    for bad in ("", "abc", "1..2", "1.0-1", "v1"):
        with pytest.raises(ValueError):
            key(bad)


def test_newest(load_exercise):
    newest = load_exercise("ex01_version").newest
    assert newest(["1.9", "1.10", "1.10rc1", "2.0a1"]) == "1.10"
    assert newest(["1.9", "1.10rc1", "2.0a1"], allow_prerelease=True) == "2.0a1"
    assert newest(["1.0a1", "1.0rc1"]) == "1.0rc1" and newest(["3.0"]) == "3.0"
    with pytest.raises(ValueError):
        newest([])


CASES = [
    ("2.7.3", ">=2,<3", True), ("3.0", ">=2,<3", False), ("2.0", ">=2,<3", True), ("1.9.9", ">=2", False),
    ("1.0", "==1", True), ("1.0.0", "==1.0", True), ("1.1", "!=1.1", False), ("1.2", "!=1.1", True),
    ("2.5.1", "==2.*", True), ("3.0", "==2.*", False), ("2.5", "!=2.*", False), ("1.5", "!=2.*", True),
    ("2.2", "~=2.2", True), ("2.9", "~=2.2", True), ("3.0", "~=2.2", False), ("2.1", "~=2.2", False),
    ("2.2.1", "~=2.2.1", True), ("2.2.9", "~=2.2.1", True), ("2.3.0", "~=2.2.1", False), ("2.2.0", "~=2.2.1", False),
    ("1.10", ">1.9", True), ("1.9", ">1.10", False), ("5", "", True), ("1.0", " >=1 , <2 ", True),
]


@pytest.mark.parametrize("version, spec, expected", CASES)
def test_satisfies(load_exercise, version, spec, expected):
    satisfies = load_exercise("ex02_specifier").satisfies
    assert satisfies(version, spec) is expected
    assert (Version(version) in SpecifierSet(spec)) is expected             # confere com a biblioteca


def test_satisfies_invalid(load_exercise):
    satisfies = load_exercise("ex02_specifier").satisfies
    for bad in ("2", "=>1", ">=", "~=2", "foo>1"):
        with pytest.raises(ValueError):
            satisfies("1.0", bad)


def test_normalize_and_parse_requirement(load_exercise):
    module = load_exercise("ex03_requirements")
    assert module.normalize_name("Django_REST.framework") == "django-rest-framework"
    assert module.normalize_name("a--b__c") == "a-b-c"
    assert module.parse_requirement("Requests[socks, security] >= 2.31, <3 ; python_version >= '3.10'  # nota") == {
        "name": "requests", "extras": ["security", "socks"], "specifier": ">=2.31,<3", "marker": "python_version >= '3.10'"}
    assert module.parse_requirement("numpy") == {"name": "numpy", "extras": [], "specifier": "", "marker": None}
    assert module.parse_requirement("rich[jupyter]~=15.0")["specifier"] == "~=15.0"
    for bad in ("", "   # só comentário", "==1.0", "bad name"):
        with pytest.raises(ValueError):
            module.parse_requirement(bad)


def test_parse_requirements_file(load_exercise):
    module = load_exercise("ex03_requirements")
    text = "# prod\nrequests==2.34.2  # exata\n\n-r other.txt\n-e ./local\nflask>=3,<4\n"
    assert [r["name"] for r in module.parse_requirements(text)] == ["requests", "flask"]
    with pytest.raises(ValueError, match="linha 3"):
        module.parse_requirements("a\nb\n==bad\n")


INDEX = {
    "app": {"1.0": {"web": ">=2", "db": ">=1"}},
    "web": {"3.0": {"core": ">=2,<3"}, "2.0": {"core": ">=1,<3"}},
    "db": {"1.1": {"core": "<2"}, "1.0": {"core": "<2"}},
    "core": {"3.0": {}, "2.5": {}, "2.0": {}, "1.9": {}},
}


def test_resolver_backtracks(load_exercise):
    resolve = load_exercise("ex04_resolver").resolve
    # web 3.0 exige core>=2; db exige core<2 -> conflito: retrocede para web 2.0
    assert resolve(INDEX, {"app": ">=1"}) == {"app": "1.0", "web": "2.0", "db": "1.1", "core": "1.9"}
    assert resolve(INDEX, {"core": ">=1"}) == {"core": "3.0"}
    assert resolve(INDEX, {"web": ">=1", "core": "<3"}) == {"web": "3.0", "core": "2.5"}


def test_resolver_errors(load_exercise):
    module = load_exercise("ex04_resolver")
    with pytest.raises(module.ResolutionError):
        module.resolve(INDEX, {"app": ">=1", "core": ">=3"})
    with pytest.raises(module.ResolutionError):
        module.resolve(INDEX, {"nope": ">=1"})
    with pytest.raises(module.ResolutionError):
        module.resolve(INDEX, {"core": ">=9"})


def lock(*pairs):
    return "version = 1\n" + "".join(f'\n[[package]]\nname = "{n}"\nversion = "{v}"\n' for n, v in pairs)


def test_lock_diff(load_exercise):
    module = load_exercise("ex05_lock_diff")
    old = lock(("a", "1.9"), ("b", "2.0"), ("c", "1.0"), ("d", "3.1"))
    new = lock(("a", "1.10"), ("b", "2.0"), ("c", "0.9"), ("e", "1.0"))
    assert module.locked_versions(old) == {"a": "1.9", "b": "2.0", "c": "1.0", "d": "3.1"}
    assert module.locked_versions("version = 1\n") == {}
    diff = module.diff_locks(old, new)
    assert diff == {"added": {"e": "1.0"}, "removed": {"d": "3.1"},
                    "upgraded": {"a": ("1.9", "1.10")}, "downgraded": {"c": ("1.0", "0.9")}}
    assert module.summarize(diff) == "1 adicionado, 1 removido, 1 atualizado, 1 rebaixado"
    assert module.summarize(module.diff_locks(old, old)) == "0 adicionados, 0 removidos, 0 atualizados, 0 rebaixados"


def test_vulnerable(load_exercise):
    vulnerable = load_exercise("ex06_audit").vulnerable
    installed = {"Requests": "2.9.0", "urllib3": "1.26.20", "Flask_Login": "0.6.3"}
    advisories = [
        {"id": "B-2", "name": "requests", "below": "2.10.0"},
        {"id": "A-1", "name": "requests", "below": "2.9.0"},          # igual: NÃO vulnerável
        {"id": "C-3", "name": "flask-login", "below": "0.6.4"},
        {"id": "D-4", "name": "absent", "below": "9.0"},
        {"id": "E-5", "name": "urllib3", "below": "1.26.20"},
    ]
    assert vulnerable(installed, advisories) == [
        {"id": "C-3", "name": "flask-login", "installed": "0.6.3", "fix": "0.6.4"},
        {"id": "B-2", "name": "requests", "installed": "2.9.0", "fix": "2.10.0"},
    ]


def test_typosquatting(load_exercise):
    module = load_exercise("ex06_audit")
    assert module.distance("kitten", "sitting") == 3 and module.distance("", "abc") == 3 and module.distance("a", "a") == 0
    popular = ["requests", "numpy", "django"]
    found = module.suspicious(["Requests", "reqeusts", "nunpy", "djang", "colorama", "numpyy"], popular)
    assert found == [("djang", "django"), ("numpyy", "numpy"), ("nunpy", "numpy")]
    assert module.suspicious(["reqeusts"], popular, max_distance=1) == []
    assert module.suspicious(["reqeusts"], popular, max_distance=2) == [("reqeusts", "requests")]
