import json

data = {"01-01-2025": "I want to kill myself", 
        "01-02-2025": "I just killed myself"}

new_note = input("add a note")

data["01-03-2025"] = new_note

with open("notes.json", "w") as file:
    json.dump(data, file)


with open("notes.json", "r") as file:
    data = json.load(file)
    print(data)


print(f"\nTodays Note: {data["01-03-2025"]}")