"""pathlib sem tocar no disco: PurePath e suas partes."""
from pathlib import PurePath, PurePosixPath, PureWindowsPath

p = PurePosixPath("/srv/app/data/report.final.tar.gz")
print(p.parts)       # ('/', 'srv', 'app', 'data', 'report.final.tar.gz')
print(p.name)        # report.final.tar.gz
print(p.stem)        # report.final.tar
print(p.suffix)      # .gz
print(p.suffixes)    # ['.final', '.tar', '.gz']
print(p.parent)      # /srv/app/data
print(list(p.parents)[:2])
print(p.with_name("other.txt"))
print(p.with_suffix(".zip"))
print(p.with_stem("backup"))
print(p.anchor, p.is_absolute())

# operador / junta partes; um componente absoluto reinicia o caminho
base = PurePosixPath("/srv/app")
print(base / "logs" / "app.log")
print(base / "/etc/hosts")

print(p.relative_to("/srv"))
print(PurePosixPath("/srv/app").is_relative_to("/etc"))
print(PurePosixPath("/a/b").relative_to("/a/c", walk_up=True))

# Windows x POSIX
w = PureWindowsPath(r"C:\Users\Ana\Docs\Notes.TXT")
print(w.drive, w.root, w.parts)
print(w.as_posix())
print(w == PureWindowsPath("c:/users/ana/docs/notes.txt"))
print(p == PurePosixPath("/SRV/app/data/report.final.tar.gz"))
print(PureWindowsPath("a/b") == PureWindowsPath(r"a\b"))

# correspondência com padrão (3.13)
print(PurePath("src/pkg/mod.py").full_match("src/**/*.py"))
print(PurePath("src/pkg/mod.py").match("*.py"))
