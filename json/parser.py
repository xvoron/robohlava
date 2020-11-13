import json

f = open('text.json',)

data = json.load(f)
print(type(data['wait']))

print(data["game"][1])
print(type(data["game"][1]))

f.close()
