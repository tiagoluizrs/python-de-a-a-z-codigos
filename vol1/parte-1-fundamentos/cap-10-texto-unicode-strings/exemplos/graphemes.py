"""len() conta pontos de código, não o que o usuário vê."""
import unicodedata as ud

samples = {
    "e acute NFC": "é",
    "e acute NFD": "e\u0301",
    "flag BR": "\U0001F1E7\U0001F1F7",
    "thumbs up tone": "\U0001F44D\U0001F3FD",
    "family": "\U0001F468\u200d\U0001F469\u200d\U0001F467",
    "hangul": "\u1112\u1161\u11ab",
    "devanagari": "\u0915\u094d\u0937\u093f",
}
for name, s in samples.items():
    clusters = list(ud.iter_graphemes(s))
    print(f"{name:15} codepoints={len(s)} utf8={len(s.encode())} "
          f"graphemes={len(clusters)}")

family = samples["family"]
print([f"U+{ord(c):04X}" for c in family])
print(family[::-1] == family, len(family[::-1]))
mixed = "ae\u0301z\U0001F1E7\U0001F1F7"
print([(g.start, g.end, str(g)) for g in ud.iter_graphemes(mixed)])

# truncar com segurança: nunca no meio de um cluster
def truncate(text, limit):
    out, count = [], 0
    for cluster in ud.iter_graphemes(text):
        if count == limit:
            break
        out.append(str(cluster))
        count += 1
    return "".join(out)

print(truncate("a\u0301bc", 2), len(truncate("a\u0301bc", 2)))
print(len("a\u0301bc"[:2]), repr("a\u0301bc"[:2]))
