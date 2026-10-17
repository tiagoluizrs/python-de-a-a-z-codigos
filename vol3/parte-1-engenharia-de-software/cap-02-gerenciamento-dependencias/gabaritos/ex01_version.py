"""Gabarito do exercício 1."""
import re

PATTERN = re.compile(r"^(\d+(?:\.\d+)*)(?:(a|b|rc)(\d+))?(?:\.post(\d+))?(?:\.dev(\d+))?$")
PRE_ORDER = {"a": 0, "b": 1, "rc": 2}


def version_key(text):
    match = PATTERN.match(text.strip())
    if not match:
        raise ValueError(f"versão inválida: {text!r}")
    release_text, pre, pre_n, post, dev = match.groups()
    release = [int(part) for part in release_text.split(".")]
    while len(release) > 1 and release[-1] == 0:
        release.pop()
    infinity = float("inf")
    if pre is None and post is None and dev is not None:
        pre_key = (-1, 0)                                   # 1.0.dev0 < 1.0a1
    elif pre is None:
        pre_key = (3, 0)                                    # final (ou post) depois de qualquer pré
    else:
        pre_key = (PRE_ORDER[pre], int(pre_n))
    post_key = int(post) if post is not None else -1
    dev_key = int(dev) if dev is not None else infinity
    return (tuple(release), pre_key, post_key, dev_key)


def newest(versions, allow_prerelease=False):
    versions = list(versions)
    if not versions:
        raise ValueError("lista vazia")
    stable = [v for v in versions if not re.search(r"(a|b|rc)\d+|\.dev\d+", v)]
    pool = versions if allow_prerelease or not stable else stable
    return max(pool, key=version_key)
