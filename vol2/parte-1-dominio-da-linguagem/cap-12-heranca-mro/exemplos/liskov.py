"""Liskov: a subclasse precisa respeitar o contrato da superclasse."""


class Rectangle:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def area(self):
        return self.width * self.height


class Square(Rectangle):
    """Um quadrado "é um" retângulo... na matemática. No código?"""

    def __init__(self, side):
        super().__init__(side, side)

    @property
    def width(self):
        return self._side

    @width.setter
    def width(self, value):
        self._side = value

    @property
    def height(self):
        return self._side

    @height.setter
    def height(self, value):
        self._side = value


def stretch(rect):
    """Contrato do Rectangle: mudar a largura NÃO altera a altura."""
    rect.width = 10
    return rect.area()


rect = Rectangle(2, 3)
print("Rectangle: 10 * 3 =", stretch(rect))
square = Square(3)
print("Square   : esperávamos 30, obtivemos", stretch(square))

# Uma forma de projetar melhor: a base comum e uma hierarquia mais honesta
class Shape:
    def area(self):
        raise NotImplementedError


class Rect(Shape):
    def __init__(self, width, height):
        self.width, self.height = width, height

    def area(self):
        return self.width * self.height


class Sq(Shape):                           # irmão, não filho
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side**2


print([shape.area() for shape in (Rect(2, 3), Sq(3))])
