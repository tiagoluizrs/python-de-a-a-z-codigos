"""Gabarito do exercício 3."""


class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Playlist(self._songs[key])            # a fatia é uma Playlist
        if not isinstance(key, int):
            raise TypeError(f"índice deve ser int ou slice, não {type(key).__name__}")
        return self._songs[key]                           # IndexError natural

    def __repr__(self):
        return f"Playlist({self._songs!r})"
