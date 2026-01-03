from .Action import Action

from .AjoutItems import AjoutItems
from .AjoutTemps import AjoutTemps
from .Boutique import Boutique
from .Combat import Combat
from .Condition import Condition
from .Damage import Damage
from .Deplacement import Deplacement
from .Dialogue import Dialogue
from .Execution import Execution
from .RandomAction import RandomAction
from .Selection import Selection
from .SelectionAction import SelectionAction

from boss.radahn import Radahn
from boss.street_fighter import StreetFighter

actions_par_type = {
    "ajout-items": AjoutItems,
    "ajout-temps": AjoutTemps,
    "boutique": Boutique,
    "combat": Combat,
    "condition": Condition,
    "damage": Damage,
    "deplacement": Deplacement,
    "dialogue": Dialogue,
    "execution": Execution,
    "random": RandomAction,
    "select": Selection,
    "selection-action": SelectionAction,

    "street-fighter": StreetFighter,
    "radahn": Radahn
}
