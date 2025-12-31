from .Action import Action


class Execution(Action):

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        assert "code" in self.data

    def executer(self):
        super().executer()
        eval(self.data.get("code"), {"jeu": self.jeu})
        self.complete = True
