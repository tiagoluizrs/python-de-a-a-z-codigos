"""Mediator, forma clássica (GoF): um objeto central COORDENA a comunicação entre colegas que não se conhecem."""
import ast
import inspect
import textwrap
import time


# --- 1. o problema: uma teia (mesh) de referências entre os componentes de um formulário ---
class MeshCheckbox:
    def __init__(self):
        self.checked, self.button = False, None            # conhece o botão

    def toggle(self):
        self.checked = not self.checked
        self.button.refresh()


class MeshTextBox:
    def __init__(self):
        self.text, self.button = "", None                  # também conhece o botão

    def type(self, text):
        self.text = text
        self.button.refresh()


class MeshButton:
    def __init__(self, checkbox, textbox):
        self.checkbox, self.textbox = checkbox, textbox    # conhece os DOIS (e eles o conhecem)
        self.enabled = False
        checkbox.button = textbox.button = self

    def refresh(self):
        self.enabled = self.checkbox.checked and "@" in self.textbox.text


box, text = MeshCheckbox(), MeshTextBox()
button = MeshButton(box, text)
box.toggle()
text.type("ana@x.com")
print("teia de referências:", button.enabled, "| o botão conhece 2 colegas e cada um deles conhece o botão: 4 ligações para 3 componentes")
print("acrescentar um campo novo (um rótulo de erro) obriga a editar o botão E os dois campos")


# --- 2. o Mediator: os componentes só conhecem o mediador; as REGRAS moram nele ---
class Component:
    def __init__(self, mediator=None):
        self.mediator = mediator

    def changed(self):
        if self.mediator:
            self.mediator.notify(self)                      # o componente só AVISA: não sabe quem reage


class Checkbox(Component):
    checked = False

    def toggle(self):
        self.checked = not self.checked
        self.changed()


class TextBox(Component):
    text = ""

    def type(self, text):
        self.text = text
        self.changed()


class Button(Component):
    enabled = False


class Label(Component):
    text = ""


class FormMediator:
    def __init__(self):
        self.agree, self.email, self.submit, self.error = Checkbox(self), TextBox(self), Button(self), Label(self)

    def notify(self, sender):                               # TODAS as regras de interação, em um lugar
        if not self.agree.checked:
            self.error.text, self.submit.enabled = "aceite os termos", False
        elif "@" not in self.email.text:
            self.error.text, self.submit.enabled = "e-mail inválido", False
        else:
            self.error.text, self.submit.enabled = "", True


form = FormMediator()
form.email.type("ana")
print("\nMediator:", repr(form.error.text), form.submit.enabled)
form.agree.toggle()
print("  aceitou os termos     ->", repr(form.error.text), form.submit.enabled)
form.email.type("ana@x.com")
print("  e-mail válido         ->", repr(form.error.text), form.submit.enabled)
print("os componentes não se conhecem (uma ligação de cada componente, só para o mediador); uma regra nova edita SÓ o mediador")

# --- 3. a armadilha: o mediador que sabe demais (o "objeto deus") e a reentrância ---
class Looping:
    def __init__(self):
        self.a = self.b = 0
        self.calls = 0

    def set_a(self, value):
        self.a = value
        self.notify("a")

    def set_b(self, value):
        self.b = value
        self.notify("b")

    def notify(self, who):
        self.calls += 1
        if self.calls > 50:
            raise RuntimeError("laço infinito entre os colegas")
        if who == "a":
            self.set_b(self.a + 1)                          # a regra de a muda b...
        else:
            self.set_a(self.b + 1)                          # ...e a de b muda a: um laço


try:
    Looping().set_a(1)
except RuntimeError as error:
    print("\nreentrância:", error, "| um mediador que reage a mudanças que ELE mesmo provoca precisa de uma guarda (só reagir se o valor mudou)")


# --- 4. a cerimônia ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nteia:", measure([MeshCheckbox, MeshTextBox, MeshButton]), "| mediador (Component + 4 componentes + FormMediator):", measure([Component, Checkbox, TextBox, Button, Label, FormMediator]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


f2 = FormMediator()
f2.agree.toggle()
print(f"digitar um e-mail (uma notificação): {best(lambda: f2.email.type('a@b')):4.0f} ns")
