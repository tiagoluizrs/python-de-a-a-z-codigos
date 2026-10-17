"""O que __getitem__ realmente recebe: int, slice, tupla, Ellipsis."""


class Spy:
    def __getitem__(self, key):
        return key


spy = Spy()
print(repr(spy[3]))
print(repr(spy[1:5]))
print(repr(spy[::2]))
print(repr(spy[1, 2]))
print(repr(spy[1:3, ::2]))
print(repr(spy[...]))
print(repr(spy[-1]))

# slice.indices adapta qualquer fatia ao tamanho do contêiner
fatia = slice(-3, None, 2)
print(fatia.indices(10), list(range(*fatia.indices(10))))
print(slice(None, 100).indices(5))


class Playlist:
    def __init__(self, songs):
        self.songs = list(songs)

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Playlist(self.songs[key])      # fatia devolve OUTRA Playlist
        return self.songs[key]                     # índice devolve o item

    def __repr__(self):
        return f"Playlist({self.songs!r})"


songs = Playlist(["a", "b", "c", "d", "e"])
print(songs[1:4], songs[::-1], songs[-1], type(songs[:2]).__name__)
try:
    songs[10]
except IndexError as error:
    print("IndexError:", error)


class Grid:
    def __init__(self, rows, cols):
        self.cells = [[0] * cols for _ in range(rows)]

    def __getitem__(self, position):
        row, col = position                        # chave composta: tupla
        return self.cells[row][col]

    def __setitem__(self, position, value):
        row, col = position
        self.cells[row][col] = value


grid = Grid(2, 3)
grid[1, 2] = 9
print(grid[1, 2], grid.cells)
