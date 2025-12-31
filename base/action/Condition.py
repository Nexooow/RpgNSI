from .Action import Action


class Condition(Action):

    def __init__(self, jeu, data):
        super().__init__(jeu, data)

    def executer(self):
        super().executer()
        result = eval(self.data.get("code", False), {
            "jeu": self.jeu,
        })
        for condition, action in self.data.get("actions", {}).items():
            if result == condition:
                self.jeu.actions.inserer(
                    list(
                        map(self.jeu.loader.creer_action, action)
                    )
                )
        self.complete = True
