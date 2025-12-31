import json
from pathlib import Path

with open(".data/lieux.json") as f:
    data = json.load(f)
    for lieu in data:
        id = lieu["id"]
        file_path = Path(f".data/npc/{id}.json")
        if file_path.is_file():
            continue
        npcData = {
            "id": lieu["id"],
            "nom": lieu["id"],
            "rencontre": [],
            "interaction": []
        }
        print(f"Json pour le npc {id} créer")
        json.dump(npcData, open(file_path, "w"))
