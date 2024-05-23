# modules/UI.py

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeView,
    QDateEdit,
    QTimeEdit,
    QDialog,
    QTextEdit,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QSize, QDate, QTime, QModelIndex
from transportDB import TransportDB
from connections import Connections
from helper import get_coordinates, get_country_name, haversine, percent_calculator
from map import Map
import qdarkstyle


class ConnectionInfoWindow(QDialog):
    def __init__(self, connection_info):
        super().__init__()
        self.setWindowTitle("Connection Information")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Information", "Departure", "Arrival", "To"])

        sections = connection_info.get("sections", [])

        for i, section in enumerate(sections):
            journey = section.get("journey", {})
            departure_info = section.get("from", {})
            arrival_info = section.get("to", {})

            if 'walk_duration' in section:
                walk_duration = section['walk_duration']
                journey_item = QStandardItem(
                    f"Walk Duration: {int(walk_duration / 60)} minutes"
                )
                departure_item = QStandardItem("-")
                arrival_item = QStandardItem("-")

                # Show the station_name of the next departure in the "To" column
                if i + 1 < len(sections):
                    next_section = sections[i + 1]
                    next_departure_info = next_section.get("from", {})
                    to_item = QStandardItem(next_departure_info.get('station_name', 'N/A'))
                else:
                    to_item = QStandardItem("N/A")
            else:
                journey_item = QStandardItem(
                    f"{journey.get('category', 'N/A')} {journey.get('number', 'N/A')}\n"
                    f"Direction: {journey.get('to', 'N/A')}"
                )
                departure_platform = departure_info.get('platform')
                arrival_platform = arrival_info.get('platform')
                departure_platform_text = departure_platform if departure_platform is not None else "-"
                arrival_platform_text = arrival_platform if arrival_platform is not None else "-"

                departure_item = QStandardItem(
                    f"{departure_info.get('station_name', 'N/A')}\n"
                    f"{departure_info.get('departure', 'N/A').split(' ')[1] if 'departure' in departure_info else 'N/A'}\n"
                    f"Platform: {departure_platform_text}"
                )
                arrival_item = QStandardItem(
                    f"{arrival_info.get('station_name', 'N/A')}\n"
                    f"{arrival_info.get('arrival', 'N/A').split(' ')[1] if 'arrival' in arrival_info else 'N/A'}\n"
                    f"Platform: {arrival_platform_text}"
                )
                to_item = QStandardItem(journey.get("to", "N/A"))

            self.model.appendRow([journey_item, departure_item, arrival_item, to_item])

        self.tree_view.setModel(self.model)
        layout.addWidget(self.tree_view)

        self.tree_view.setColumnWidth(0, 150)
        self.tree_view.setColumnWidth(1, 150)
        self.tree_view.setColumnWidth(2, 150)
        self.tree_view.setColumnWidth(3, 150)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Transport Search")
        self.setMinimumSize(QSize(800, 600))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.connection_info = []
        self.departure = ""
        self.destination = ""
        self.country = ""
        self.status_text = ""
        self.db = TransportDB()

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        input_layout = QVBoxLayout()
        layout.addLayout(input_layout)

        from_to_layout = QHBoxLayout()
        input_layout.addLayout(from_to_layout)

        departure_label = QLabel("From:")
        from_to_layout.addWidget(departure_label)

        self.departure_input = QLineEdit()
        self.departure_input.textChanged.connect(self.check_input_fields)
        from_to_layout.addWidget(self.departure_input)

        to_label = QLabel("To:")
        from_to_layout.addWidget(to_label)

        self.destination_input = QLineEdit()
        self.destination_input.textChanged.connect(self.check_input_fields)
        from_to_layout.addWidget(self.destination_input)

        date_time_layout = QHBoxLayout()
        input_layout.addLayout(date_time_layout)

        date_label = QLabel("Date:")
        date_time_layout.addWidget(date_label)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        date_time_layout.addWidget(self.date_input)

        time_label = QLabel("Time:")
        date_time_layout.addWidget((time_label))

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        date_time_layout.addWidget(self.time_input)

        self.search_button = QPushButton("Search Connections")
        self.search_button.clicked.connect(self.search_connections)
        self.search_button.setEnabled(False)
        input_layout.addWidget(self.search_button)

        self.result_tree = QTreeView()
        self.result_tree.setFixedHeight(200)
        self.result_model = QStandardItemModel()
        self.result_model.setHorizontalHeaderLabels(["Information", "Departure", "Arrival", "Duration", "Transfers"])
        self.result_tree.setModel(self.result_model)
        self.result_tree.clicked.connect(self.show_connection_info)
        layout.addWidget(self.result_tree)

        self.result_tree.setColumnWidth(0, 250)
        self.result_tree.setColumnWidth(1, 120)
        self.result_tree.setColumnWidth(2, 120)
        self.result_tree.setColumnWidth(3, 100)
        self.result_tree.setColumnWidth(4, 60)

        status_label = QLabel("Status Information")
        layout.addWidget(status_label)

        self.status_info = QTextEdit()
        self.status_info.setReadOnly(True)
        self.status_info.setFixedHeight(200)
        layout.addWidget(self.status_info)

        self.map_button = QPushButton("View Map")
        self.map_button.clicked.connect(self.get_map)
        self.map_button.setEnabled(False)
        input_layout.addWidget(self.map_button)

    def check_input_fields(self):
        if self.departure_input.text().strip() and self.destination_input.text().strip():
            self.search_button.setEnabled(True) and self.map_button.setEnabled(True)
        else:
            self.search_button.setEnabled(False) and self.map_button.setEnabled(False)

    # Update destination logic if not reachable, update status info aswell
    def search_connections(self):

        self.departure = self.departure_input.text().strip()
        self.destination = self.destination_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")

        if self.departure and self.destination:
            # Check blacklist before initiating a web query
            blacklist_entry = self.db.check_blacklist(self.departure, self.destination)

            if not blacklist_entry:
                self.map_button.setEnabled(True)
                con = Connections(self.departure, self.destination, date, time)
                connections_info = con.connection_data_extraction()
                self.connection_info = connections_info
                self.result_model.removeRows(0, self.result_model.rowCount())

                if connections_info:
                    self.status_text = "Connection found!"
                    self.update_status_info()
                    for connection in connections_info:
                        products = connection.get("products", [])
                        products_text = ", ".join(products)
                        to_name = connection["to"]["name"]
                        from_departure = connection["from"]["departure"]
                        to_arrival = connection["to"]["arrival"]
                        duration = connection["duration"]
                        transfers = str(connection["transfers"])

                        connection_item = QStandardItem(f"{products_text}\nTo {to_name}")
                        self.result_model.appendRow([
                            connection_item,
                            QStandardItem(from_departure),
                            QStandardItem(to_arrival),
                            QStandardItem(duration),
                            QStandardItem(transfers)
                        ])
                else:
                    # Extract coordinates
                    cities = self.extract_coordinates()

                    # Write connection with all necessary data into blacklist
                    self.db.add_blacklist_entry(self.departure, self.destination, cities[0][1], cities[0][0], cities[1][1], cities[1][0], self.country, db.get_web_link(self.country))
                    self.result_model.removeRows(0, self.result_model.rowCount())
                    self.status_text = ("No direct Connection available\n"
                                        "Press 'View Map' for further Information")
                    self.update_status_info()

            else:
                self.status_text = blacklist_entry["info_text"]
                self.update_status_info()

    def show_connection_info(self, index: QModelIndex):
        selected_row = index.row()
        selected_connection = self.connection_info[selected_row]
        info_window = ConnectionInfoWindow(selected_connection)
        info_window.exec()

    def update_status_info(self):
        self.status_info.setPlainText(self.status_text)

    def Blacklist_entry_text(self):
        pass

    def extract_coordinates(self):
        cities = []
        if self.connection_info:
            lat_dep = self.connection_info[0]['from']["location"].get("x")
            lon_dep = self.connection_info[0]['from']["location"].get("y")
            lat_des = self.connection_info[0]['to']["location"].get("x")
            lon_des = self.connection_info[0]['to']["location"].get("y")

            cities.append((float(lat_dep), float(lon_dep)))
            cities.append((float(lat_des), float(lon_des)))
            print(cities)
            return cities
        else:
            print(self.departure)
            print(self.destination)
            lat_dep, lon_dep = get_coordinates(self.departure)
            lat_des, lon_des = get_coordinates(self.destination)
            self.country = get_country_name(lat_des, lon_des)
            cities.append((float(lat_dep), float(lon_dep)))
            cities.append((float(lat_des), float(lon_des)))
            return cities

    def get_map(self):
        cities = self.extract_coordinates()
        cone_map = Map(cities)
        reachable = cone_map.reacheables

        closest_city = cone_map.get_closest_city()
        print(closest_city)
        if reachable:
            closest_city_name = closest_city[1]
            lon, lat = get_coordinates(closest_city_name)
            missing_distance = int(closest_city[0])
            reachable_distance = haversine(cities[0][0], cities[0][1], lon, lat)
            total_distance, reachable_percent, leftover_percent = percent_calculator(reachable_distance, missing_distance)
            info_text = "Reachable Locations are:\n"
            for location in reachable:
                if location['name'] == closest_city[1]:
                    info_text += f"Closest: {str(location['name'])}, covers {round(reachable_percent)}% of the distance\n"
                else:
                    info_text += f"{str(location['name'])}\n"
        else:
            info_text = ("Apologizes!\n"
                         "No reachable Connections found!")
        web_site = self.db.get_web_link(self.country)
        if web_site:
            info_text += (f"Check Connection to {closest_city[1]} for more Information about Travel time.\n"
                          f"Check Connection from {closest_city[1]} to {self.destination} at:\n"
                          f"{web_site}")
        self.status_text = info_text
        self.db.update_blacklist(self.departure, self.destination, info_text)
        self.update_status_info()


if __name__ == "__main__":
    app = QApplication([])

    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()
