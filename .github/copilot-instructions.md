# Copilot instructions for RpgNSI

This file gives focused, actionable guidance to an AI coding agent working on this repository.

1) Big picture
- The project is a Pygame-based single-player RPG. The main loop is in `main.py` and the core game class is `Jeu` in `Jeu.py`.
- Data-driven game logic: behavior and sequences are defined as JSON under `./.data/` (notably `./.data/actions/`, `./.data/npc/`, `./.data/items/`, and `./.data/lieux.json`). `base/JSONLoader.py` loads these at startup and instantiates `Action` objects.

2) Entrypoints & run commands
- Install dependencies: `pip install -r requirements.txt`.
- Run the game with: `python main.py` (the Pygame loop is started here).

3) Key components and where to look
- `Jeu.py`: game state, main update loop (`gerer_evenement`, `executer`, `scene`), action queue management, and save/restore (`sauvegarder`, `restaurer`).
- `base/JSONLoader.py`: loads JSON sequences and maps `type` → Action subclass via `actions_par_type`.
- `base/action/`: action implementations. New JSON action types must map to classes in `base/action/__init__.py` (see `actions_par_type`).
- `lib/file.py`: simple FIFO queue used for action scheduling (`enfiler`, `defiler`, `inserer`, `est_vide`).
- `.data/actions/*.json`: define sequences. Each file must be a dict with `id`, `type` and `run` (list of action dicts). Action dicts must include `type` which maps to a class in `base/action`.

4) JSON / action conventions (concrete examples)
- Example sequence file location: `./.data/actions/test_combat.json` — sequences are loaded by `JSONLoader.charger_actions()` and stored by `id`.
- Action JSON example (minimal):
  {
    "type": "ajout-temps",
    "temps": 1
  }
- When creating a new action type:
  - Add a class file under `base/action/` implementing the `Action` interface (`Action.py`).
  - Import and add it to `actions_par_type` in `base/action/__init__.py`.
  - JSON sequences can then reference it by its `type` string.

5) Patterns & conventions to preserve
- Game flow is queue-driven: `Jeu.executer()` pulls `Action` instances from the `File` queue and calls `executer()` / `update()` / `draw()` on them. Avoid changing that contract unless updating all actions.
- Use `JSONLoader.creer_action(data)` to instantiate actions from saved data or JSON; saved game state stores action `.data` which the loader converts back to objects.
- File I/O uses `./.data/` (saves `./.data/saves/`, actions `./.data/actions/`, items and npc under `.data/`). Keep that structure.

6) Debugging & development tips
- Use the console prints (many loaders and `Jeu` methods print messages) — running `python main.py` provides helpful runtime logs.
- To add quick scenarios, create new JSON sequences in `./.data/actions/` and call `Jeu.executer_sequence("your_id")` from code or start a game that triggers it.

7) Common pitfalls
- JSON action objects must include a valid `type` matching `actions_par_type`; otherwise `JSONLoader.creer_action` returns `None` and an error is printed.
- Action classes often expect `parent` (the `Jeu` instance) and a `data` dict in the constructor — follow existing constructors.

If anything here is unclear or you want the doc to include additional examples (e.g., a concrete `test_combat.json` walkthrough or step-by-step for adding a new NPC), tell me which part to expand.
