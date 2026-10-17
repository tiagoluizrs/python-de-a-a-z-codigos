"""Gabarito do exercício 1."""


class Component:
    def __init__(self, mediator=None):
        self.mediator = mediator

    def changed(self):
        if self.mediator is not None:
            self.mediator.notify(self)


class Checkbox(Component):
    checked = False

    def toggle(self):
        self.checked = not self.checked
        self.changed()

    def set(self, value):
        if self.checked != value:
            self.checked = value
            self.changed()


class TextBox(Component):
    text = ""

    def type(self, text):
        if text != self.text:
            self.text = text
            self.changed()


class Button(Component):
    enabled = False
    clicks = 0

    def click(self):
        if not self.enabled:
            raise RuntimeError("botão desabilitado")
        self.clicks += 1
        self.changed()
        if self.mediator is not None:
            return self.mediator.submitted()
        return None


class Label(Component):
    text = ""


class FormMediator:
    def __init__(self):
        self.submissions = []
        self.agree, self.email = Checkbox(self), TextBox(self)
        self.submit, self.error = Button(self), Label(self)
        self.notify(self.agree)

    def notify(self, sender):
        if sender is self.submit or sender is self.error:
            return
        text = self.email.text
        valid = "@" in text and not text.startswith("@") and not text.endswith("@")
        if not self.agree.checked:
            self.error.text, self.submit.enabled = "aceite os termos", False
        elif not valid:
            self.error.text, self.submit.enabled = "e-mail inválido", False
        else:
            self.error.text, self.submit.enabled = "", True

    def submitted(self):
        data = {"email": self.email.text}
        self.submissions.append(data)
        return data
