"""Gabarito do exercício 3."""
import ntpath
import posixpath

FAMILIES = {"posix": posixpath, "nt": ntpath}


def family_for(system):
    try:
        return FAMILIES[system.lower()]
    except KeyError:
        raise ValueError(f"sistema desconhecido: {system!r}") from None


def portable_join(system, *parts):
    if not parts:
        raise ValueError("sem partes")
    return family_for(system).join(*parts)


def describe(system):
    fam = family_for(system)
    return {"sep": fam.sep, "case_sensitive": fam.normcase("A") == "A", "has_drive": fam.splitdrive("C:/x")[0] == "C:"}


def same_file(system, a, b):
    fam = family_for(system)
    return fam.normcase(fam.normpath(a)) == fam.normcase(fam.normpath(b))
