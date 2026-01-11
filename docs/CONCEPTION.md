# Document de Conception - Projet RPG

## Vue d'ensemble

### Description générale

Ce projet est un **RPG** développé en **Python** avec **Pygame**.

### But du jeu

Le joueur doit vaincre les trois boss (Simon, Radahn et Demiurge) pour récupérer trois doigts.

### Déroulement type

Le joueur commence dans une auberge, explore pour recruter des alliés, améliore son équipement et affronte des boss dans
différentes régions.
Lors de ses déplacements, il rencontre des PNJ, participe à des combats au tour par tour, et progresse dans l'histoire.

---

## Composants principaux

### 1. Classe Jeu (Jeu.py)

**Rôle:** Orchestrateur central du jeu

- Gestion de l'état global du jeu
- Gestion de la file d'actions
- Gestion de la région et du lieu actuels
- Gestion du temps de jeu
- Gestion de la musique et des effets sonores
- Coordination entre menu et gameplay

**Attributs clés:**

```
- WIDTH, HEIGHT (1000x700)
- running: bool (état du jeu)
- debute: bool (jeu démarré)
- fond: pygame.Surface (fond du jeu)
- ui_surface: pygame.Surface (interface utilisateur)
- filter_surface: pygame.Surface (filtres/effets)
- action_actuelle: Action (action en cours)
- actions: File (file d'attente d'actions)
- equipe: Equipe (équipe du joueur)
- regions: dict (régions du monde)
- region: str (région actuelle)
- lieu: str (lieu actuel)
- temps: int (temps de jeu en heures)
- variables_jeu: dict (variables de jeu dynamiques)
```

**Méthodes principales:**

- `demarrer(identifiant, save_json)` : Démarre une partie
- `sauvegarder()` : Sauvegarde l'état du jeu
- `restaurer(save_json)` : Restaure une partie sauvegardée
- `gerer_evenement(evenements)` : Traite les événements
- `executer()` : Gère la boucle d'exécution des actions
- `scene()` : Rendu de la scène actuelle
- `jouer_musique(nom, loop, volume)` : Gère la musique

### 2. Classe Personnage (base/Personnage.py)

**Rôle:** Représentation des personnages du jeu

- Gestion des attributs et statistiques
- Gestion des animations et sprites
- Gestion des compétences et équipement
- Calcul des dégâts et défense
- Progression et expérience

**Attributs clés:**

```
- nom: str
- niveau: int
- xp: int
- attributs: dict {
    "vie_max": int,
    "vie": int,
    "force": int,
    "vitesse": int,
    "chance_critique": int
  }
- competences: dict (compétences équipées)
- arme: dict (arme équipée)
- animation_list: list (frames d'animation)
- action: int (animation courante)
- frame_index: int (frame courante)
- effets: dict (effets actifs)
```

**Sous-classes:**

- `Vous` : Personnage principal jouable
- `Barman` : PNJ allié
- `Fachan` : allié (deux formes : normale et acier)

### 3. Classe Équipe (base/Equipe.py)

**Rôle:** Gestion de l'équipe du joueur

- Gestion des personnages dans l'équipe
- Gestion de l'inventaire
- Gestion de l'argent et des ressources

**Attributs clés:**

```
- personnages: list[Personnage]
- inventaire: dict (items et quantités)
- argent: int
- chance: int
```

### 4. Classe Region (base/Region.py)

**Rôle:** Représentation d'une région du monde

- Gestion des lieux dans la région
- Gestion de la carte locale (graphe)
- Gestion des paramètres régionaux (musique, fond)

**Attributs clés:**

```
- nom: str (nom de la région)
- lieux: dict (lieux disponibles)
- entree: str (lieu d'entrée par défaut)
- carte: Graph (graphe de la région)
- position: tuple (position sur la carte mondiale)
- modificateur_chance: float
```

**Régions existantes:**

- Auberge (taverne, point de départ)
- Mountain (montagne)
- Ceilidh (région mystique)
- Dawn of the world (aube du monde)
- Elder Tree (arbre ancien)

### 5. Classe Action (base/action/Action.py)

**Rôle:** Classe de base pour toutes les actions  
**Responsabilités:**

- Définition de l'interface d'action
- Gestion du cycle de vie (exécution, mise à jour, rendu)
- Gestion des flags (utilise_musique, utilise_fond, desactive_ui)

**Méthodes principales:**

```
def executer(self):  # Appelée au démarrage de l'action
def update(self, events):  # Mise à jour selon événements
def draw(self):  # Rendu
def get_complete(self) -> bool:  # Retourne si action terminée
```

**Types d'actions implémentées:**

| Type               | Classe          | Utilité                              |
|--------------------|-----------------|--------------------------------------|
| `combat`           | Combat          | Gestion des combats au tour par tour |
| `dialogue`         | Dialogue        | Affichage de dialogues               |
| `deplacement`      | Deplacement     | Déplacement entre lieux              |
| `ajout-temps`      | AjoutTemps      | Progression du temps                 |
| `ajout-items`      | AjoutItems      | Ajout d'items à l'inventaire         |
| `boutique`         | Boutique        | Système de magasin                   |
| `damage`           | Damage          | Infliction de dégâts                 |
| `condition`        | Condition       | Branchement conditionnel             |
| `selection-action` | SelectionAction | Menu de sélection d'actions          |
| `execution`        | Execution       | Exécution d'une séquence             |
| `random`           | RandomAction    | Choix aléatoire d'actions            |
| `select`           | Selection       | Sélection dans un menu               |
| `add_perso`        | AddPerso        | Ajout de personnage à l'équipe       |
| `radahn`           | Radahn          | Boss fight (combat contre Radahn)    |
| `street-fighter`   | StreetFighter   | Boss fight                           |

### 6. Classe Loader (base/Loader.py)

**Rôle:** Chargement dynamique des ressources

- Chargement des actions depuis JSON
- Chargement des items depuis JSON
- Chargement des NPCs depuis JSON
- Chargement des régions
- Création d'instances d'actions

**Structure des fichiers chargés:**

- `.data/actions/` : Définitions des séquences d'actions
- `.data/items/` : Définitions des items
- `.data/saves/` : Fichiers de sauvegarde

### 7. Classe Graph (lib/graph.py)

**Rôle:** Implémentation d'un graphe pondéré

- Représentation des connexions entre lieux/régions
- Calcul de trajectoires et affichage

**Utilisation:**

- Graphe global : connexions entre 5 régions
- Graphe régional : connexions entre lieux dans une région

---

## Fonctionnalités

- Déplacement inter régions et lieux
- Système de combat au tour par tour
- Gestion d'inventaire et boutique
- Système de progression et expérience
- Compétences et équipements
- Sauvegarde et restauration de parties

### Fonctionnalités tentés

- Animation des compétences: on a tenté d'animer les compétences et d'ajouter les effets lorsque celles-ci sont
  utilisées en combat. Cependant, faute de temps, nous n'avons pas pu finaliser cette fonctionnalité.