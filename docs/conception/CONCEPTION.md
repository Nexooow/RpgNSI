# Comment lancer le jeu ? 

Installer les dépendances nécessaires en utilisant pip :
```
pip install -r requirements.txt
```
Ensuite, exécuter le jeu en utilisant la commande suivante :
```
python main.py
```

# Carte

Voir image jointe
A noter que chaque région sur cette carte dispose elle même d'une carte qui permet de naviguer entre les lieux de la région.

# Univers & but

Toute resemblance avec le jeu "Elden Ring" est purement fortuite.

Le jeu se déroule dans le monde d'un ancien empire qui a été détruit par une guerre interne.
Le but est de retrouver *insérer nom de grand méchant* et de le vaincre.

# Comment se déroule la partie ?

Le joueur se déplace entre régions, puis entre lieux dans chaque région.
Cependant, chaque trajet est une aventure qui peut changer la suite de la partie.
Le joueur doit aussi gérer le temps, et ses ressources.
En effet, chaque trajet prend du temps, et vous ne voulez pas vous déplacer en pleine nuit ...
Le joueur peut également explorer les lieux et rencontrer des PNJ pour obtenir des informations ou des objets.

# Diagramme de classe

### Classe Jeu:
* identifiant: string
* joueur: Joueur
* scenes: File (contenant des listes)
File qui contient les scènes, chaque scène est une liste de classes (générées à partir d'un fichier JSON)
Ces classes sont ensuite générées sur la fenêtre pygame
* carte: Graphe
* loader: JSONLoader
* regions: dict<string, Region>
* region: string
Region actuelle ou "voyage" si le joueur est en deplacement
* lieu: string
Lieu actuel dans la région
* jour: int 
* heure: int
* minutes: int

* **init(self, identifiant: string, json?: dict)**
Utilise le loader pour charger toutes les actions et NPC du jeu, ainsi que les informations du joueur et de la partie depuis un fichier JSON
* **gerer_evenement(self, evenement)**
Gère les événements pygame et les interactions avec le joueur
ex: touches pressées ...
* **show_scene(self)**
Ne renvoie rien, mais affiche la scène actuelle sur la fenêtre pygame
Executée à chaque frame
* **deplacement(self, lieu: string, est_region: bool = false)**
Ne renvoie rien, mais ajoute des scènes à la file et met à jour les informations du joueur et de la partie
si est_region est vrai, déplacement entre région, sinon déplacement entre lieu
Pour chaque heure que prend le déplacement, on tire un evenement avec JSONLoader#tirer_action
* **save(self)**
Ne renvoie rien, mais sauvegarde les informations du joueur et de la partie dans un fichier JSON
---

### Classe JSONLoader
* parent: Jeu
* actions: dict<string, Action>
* npcs: dict<string, NPC>

* **init(self)**
Charge toutes les actions codées en JSON depuis le dossier "data/actions" ainsi que les NPC depuis le dossier "data/npcs"
les ajoute à la liste des actions ou NPC, ainsi que dans les listes d'actions par région et lieu
* **charger_NPC(self, json: dict)**
Charge les NPC à partir d'un dictionnaire JSON
* **charger_action(self, json: dict)**
Charge une action à partir d'un dictionnaire JSON
* **tirer_action(self, chance_evenement?: float, chance_evenement_negatif?: float)**
Tire une action aléatoire en fonction des chances données lors des déplacements du joueur (lors de déplacements, le joueur peut être affecté par des événements négatifs ou positifs)
---

### Classe Action
* type: string
* nom: string
* sous_actions: list<string>
* data: dict
Données de l'événement en cours d'exécution

* **init(self, json: dict)**
Initialise l'action à partir d'un dictionnaire JSON
* **executer(self)**
Execute l'action
* **draw(self)**
Affiche l'action sur l'écran
ex: si l'action est un dialogue, on affiche le texte du dialogue
* **est_complete(self)**
Renvoie True si l'action est terminée, False sinon
ex: un dialogue est terminé lorsque le joueur confirme avec 'espace'
---

### Classe NPC
* nom: string

* **init(self, json: dict)**
Initialise le NPC à partir d'un dictionnaire JSON
* **interagir(self)**
Execute l'interaction avec le NPC
---

### Classe Region
* nom: string
* description: string
* lieux: Graphe
* lieu_depart: string

* **init(self, parent: Jeu)**
* **rentrer(self)**
Execute les actions de la région lorsque le joueur entre dans la région
ex: le joueur rencontre un ennemi lors de son arrivée
* **quitter(self)**
Execute les actions de la région lorsque le joueur quitte la région
---

### Classe Lieu
* nom: string
* description?: string
* npc: list<string>

* **init(self, parent: Region, json?: dict)**
* **recuperer_actions(self)**
Renvoies les actions ou interactions possibles dans le lieu
* **executer_action(self, action: string)**
Execute l'action correspondante si elle existe en utilisant le gestionnaire d'actions
---

### Classe Joueur
* parent: Jeu
* vie: int
* vie_max: int
* defense: int
* agilite: int
* energie: int
* chance: int
* inventaire: list<tuple<Item, int>>
* objets_equipes: dict<string, string>

* **init(self, parent: Jeu, json?: dict)**
Définit les attributs du joueur à partir du fichier JSON si il est fourni (on restaure les attributs de la partie)
* **ajouter_item(self, item: string, quantite: int)**
Renvoie la nouvelle quantité
* **retirer_item(self, item: string, quantite?: int)**
Renvoie la nouvelle quantité
* **infliger(self, degats: int)**
Diminue la vie du joueur et renvoie la nouvelle vie
* **soigner(self, points: int)**
Augmente la vie du joueur et renvoie la nouvelle vie
* **calculer_degats(self)**
Renvoie le nombre de dégâts que le joueur inflige (prend en compte l'energie, potentiellement la chance et l'inventaire)
---

### Classe Item
* type: string
Type de l'item; arme, armure, objet, potion...
* nom: string
* description: string
* rarete: string
* attributs: dict<string, int>
Attributs que l'item apporte au joueur quand porté
si la valeur est positive, l'item augmente les attributs du joueur
si la valeur est négative, l'item diminue les attributs du joueur
* **init(self, type: str, nom: str, description: str, rarete: str, attributs: dict<string, int>)**