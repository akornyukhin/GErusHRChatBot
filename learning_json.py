import json

write_data = {"ID": 1, "QorA": "Q", "Content": "What do you want to know?", "Answer":{"1": 1, "2": 2}}
read_data = {}

with open('data_write.json', 'w') as outfie:
    json.dump(write_data, outfie, indent=4)

with open('data_read.json', 'r') as infile:
    read_data = json.load(infile)

print(read_data)