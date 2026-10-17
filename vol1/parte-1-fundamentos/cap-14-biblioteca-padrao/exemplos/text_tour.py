"""textwrap, difflib, unicodedata, string."""
import difflib
import string
import textwrap
import unicodedata

text = "A biblioteca padrão do Python traz baterias inclusas."
print(textwrap.fill(text, width=24))
print(textwrap.shorten(text, width=30, placeholder="..."))
print(textwrap.dedent("""\
    linha 1
      linha 2"""))

old = ["a", "b", "c"]
new = ["a", "x", "c", "d"]
print("\n".join(difflib.unified_diff(old, new, "old", "new", lineterm="")))
print(difflib.get_close_matches("pythn", ["python", "pyton", "java"]))
print(round(difflib.SequenceMatcher(None, "kitten", "sitting").ratio(), 3))

print(unicodedata.name("ç"), unicodedata.category("ç"))
nfd = unicodedata.normalize("NFD", "ç")
print(len(nfd), nfd == "ç", unicodedata.normalize("NFC", nfd) == "ç")
print(string.ascii_lowercase[:5], string.digits, len(string.punctuation))
print(string.Template("Olá, $name!").substitute(name="Ana"))
