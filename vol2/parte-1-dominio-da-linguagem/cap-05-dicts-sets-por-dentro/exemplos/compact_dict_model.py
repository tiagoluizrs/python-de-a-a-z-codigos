"""Modelo didatico do dict compacto, em Python puro.

Duas estruturas, como no CPython: uma tabela esparsa de INDICES e um
vetor denso de ENTRADAS em ordem de insercao. Aceita so chaves que
tenham hash estavel (usamos hash() direto) e nao tem tipos especiais
para str. A cena toda e para estudo: ver `compare_with_cpython`.
"""
EMPTY, DUMMY = -1, -2
PERTURB_SHIFT = 5
MASK64 = (1 << 64) - 1


class CompactDict:
    def __init__(self):
        self._new_table(8)

    def _new_table(self, slots, entries=()):
        self.slots = slots
        self.indices = [EMPTY] * slots
        self.entries = []                    # lista de [hash, key, value]
        self.usable = (slots * 2) // 3       # fator de carga maximo 2/3
        for h, key, value in entries:
            self._append(h, key, value)

    def _probe(self, h):
        """Gera as posicoes visitadas para o hash h (sequencia do CPython)."""
        mask = self.slots - 1
        perturb = h & MASK64
        i = h & mask
        while True:
            yield i
            perturb >>= PERTURB_SHIFT
            i = (i * 5 + perturb + 1) & mask

    def _find(self, key, h):
        """Devolve (slot, indice_da_entrada) ou (slot_livre, EMPTY)."""
        first_free = None
        for slot in self._probe(h):
            ix = self.indices[slot]
            if ix == EMPTY:
                return (first_free if first_free is not None else slot), EMPTY
            if ix == DUMMY:
                if first_free is None:
                    first_free = slot
                continue
            eh, ek, _ = self.entries[ix]
            if ek is key or (eh == h and ek == key):
                return slot, ix

    def _append(self, h, key, value):
        slot = next(s for s in self._probe(h)
                    if self.indices[s] < 0)          # vazio ou dummy
        self.indices[slot] = len(self.entries)
        self.entries.append([h, key, value])
        self.usable -= 1

    def _resize(self):
        live = [e for e in self.entries if e is not None]
        want = max(8, len(live) * 3)                # crescimento: used * 3
        slots = 8
        while slots < want:
            slots *= 2
        self._new_table(slots, live)

    def __setitem__(self, key, value):
        h = hash(key)
        slot, ix = self._find(key, h)
        if ix != EMPTY:
            self.entries[ix][2] = value
            return
        if self.usable <= 0:
            self._resize()
        self._append(h, key, value)

    def __getitem__(self, key):
        slot, ix = self._find(key, hash(key))
        if ix == EMPTY:
            raise KeyError(key)
        return self.entries[ix][2]

    def __delitem__(self, key):
        slot, ix = self._find(key, hash(key))
        if ix == EMPTY:
            raise KeyError(key)
        self.indices[slot] = DUMMY          # lapide na tabela esparsa
        self.entries[ix] = None             # buraco no vetor denso

    def __len__(self):
        return sum(e is not None for e in self.entries)

    def __iter__(self):
        return (e[1] for e in self.entries if e is not None)


def compare_with_cpython(ops):
    """Aplica `ops` ao modelo e a um dict real; compara a tabela."""
    from dictpeek import inspect_dict
    model, real = CompactDict(), {}
    for op, key in ops:
        if op == "set":
            model[key] = key
            real[key] = key
        elif key in real:
            del model[key]
            del real[key]
    info = inspect_dict(real)
    same_indices = info["indices"] == model.indices
    same_order = list(real) == list(model)
    return same_indices, same_order, model.slots, info["slots"]
