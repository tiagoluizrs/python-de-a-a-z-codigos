"""Gabarito do exercício 3."""
import copy


def num(value):
    return f"{value:g}"


class SvgRenderer:
    def circle(self, x, y, r):
        return f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}"/>'

    def rect(self, x, y, w, h):
        return f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}"/>'


class TextRenderer:
    def circle(self, x, y, r):
        return f"circle at ({num(x)}, {num(y)}) radius {num(r)}"

    def rect(self, x, y, w, h):
        return f"rect at ({num(x)}, {num(y)}) size {num(w)}x{num(h)}"


def _check_factor(factor):
    if factor <= 0:
        raise ValueError("fator inválido")


class Shape:
    def __init__(self, renderer):
        self.renderer = renderer

    def with_renderer(self, renderer):
        clone = copy.copy(self)
        clone.renderer = renderer
        return clone

    def draw(self):
        raise NotImplementedError

    def area(self):
        raise NotImplementedError

    def scale(self, factor):
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, renderer, x, y, r):
        super().__init__(renderer)
        if r <= 0:
            raise ValueError("raio inválido")
        self.x, self.y, self.r = x, y, r

    def draw(self):
        return self.renderer.circle(self.x, self.y, self.r)

    def area(self):
        return 3.141592653589793 * self.r ** 2

    def scale(self, factor):
        _check_factor(factor)
        return Circle(self.renderer, self.x, self.y, self.r * factor)


class Rectangle(Shape):
    def __init__(self, renderer, x, y, w, h):
        super().__init__(renderer)
        if w <= 0 or h <= 0:
            raise ValueError("tamanho inválido")
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self):
        return self.renderer.rect(self.x, self.y, self.w, self.h)

    def area(self):
        return self.w * self.h

    def scale(self, factor):
        _check_factor(factor)
        return Rectangle(self.renderer, self.x, self.y, self.w * factor, self.h * factor)


class Group(Shape):
    def __init__(self, renderer, shapes):
        super().__init__(renderer)
        self.shapes = list(shapes)

    def draw(self):
        return "\n".join(shape.draw() for shape in self.shapes)

    def area(self):
        return sum(shape.area() for shape in self.shapes)

    def scale(self, factor):
        _check_factor(factor)
        return Group(self.renderer, [shape.scale(factor) for shape in self.shapes])

    def with_renderer(self, renderer):
        return Group(renderer, [shape.with_renderer(renderer) for shape in self.shapes])
