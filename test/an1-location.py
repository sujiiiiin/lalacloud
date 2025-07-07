import json
import matplotlib.pyplot as plt
import numpy as np

dic = {}


def count_locations(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    dic = {}
    for ats in data:
        loc = ats["std_location"]
        if loc in dic:
            dic[loc] += 1
        else:
            dic[loc] = 1

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(dic, file, ensure_ascii=False, indent=4)


def draw(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cities = list (data.keys())
    val = list (data.values())

    plt.bar(cities,val)
    plt.show()


# count_locations("singer_birthplaces.json", "an1-outcome.json")

draw("an1-outcome.json")
