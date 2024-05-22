# modules/csv_reader.py

import csv


# TODO: Change to CSV Reader Class, maybe merge the functions to one
def read_csv(filename, header=True):
    output = []
    with open(f"../src/{filename}", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        if header:
            next(reader, None)

        for row in reader:
            output.append(row)
    return output


def get_base_cities():
    base_cities = []
    with open("../src/cities.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            base_cities.append(row)
    return base_cities


def get_countries():
    country_list = []
    with open("../src/countries.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            country_list.append(row)
    return country_list
