# Main file for INFPROG2 P05 – Individual Application Project
# Variant: Public Transport Routing in Europe
import qdarkstyle
from PySide6.QtWidgets import QApplication

# Authors: Vincent Pelichet, Andreas Rudolf, Andreas Urben

# Imports
from modules.UI import MainWindow


def main():
    app = QApplication([])

    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
