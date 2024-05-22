# Main file for INFPROG2 P05 – Individual Application Project
# Variant: Public Transport Routing in Europe

# Authors: Vincent Pelichet, Andreas Rudolf, Andreas Urben

# Imports
import sys
import os
from modules import locations, connections
from modules.connections import Connections
from modules.UI import MainWindow
from PySide6.QtWidgets import QApplication
import csv

current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, "modules")
sys.path.append(modules_dir)


class Application:
    def __init__(self):
        app = QApplication([])
        main_window = MainWindow()
        main_window.show()
        app.exec()


def main():
    Application()


if __name__ == '__main__':
    main()
