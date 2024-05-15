# Main file for INFPROG2 P05 – Individual Application Project
# Variant: Public Transport Routing in Europe

# Authors: Vincent Pelichet, Andreas Rudolf, Andreas Urben

# Imports
from modules import locations, connections, UI
from PySide6.QtWidgets import QApplication
import csv


def read_key_cities():
    key_cities = []

    with open("src/cities_stations.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            key_cities.append(row)

    return key_cities


class Application:
    def __init__(self):
        app = QApplication([])
        window = UI.MainWindow()
        window.show()
        app.exec()


def main():
    app = Application()


if __name__ == '__main__':
    main()
