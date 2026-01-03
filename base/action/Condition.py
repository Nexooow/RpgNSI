from .Action import Action


class Condition(Action):

    def __init__(self, jeu, data):
        super().__init__(jeu, data)

    def executer(self):
        super().executer()
        result = eval(self.data.get("code", False), {
            "jeu": self.jeu,
        })
        self.jeu.variables_jeu['Termine'] = False
        for condition, action in self.data.get("actions", {}).items():
            condition_remplie = eval(condition, {"jeu": self.jeu, "result": result})
            if condition_remplie:
                self.jeu.actions.inserer(
                    list(
                        map(self.jeu.loader.creer_action, action)
                    )
                )
        self.complete = True
