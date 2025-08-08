import json

data = {str(i): False for i in range(1, 3119)}  # De "1" à "3118"
with open("etat_disponibilite.json", "w") as f:
    json.dump(data, f, indent=2)