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
from connections import Connections
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
        self.setMinimumSize(QSize(700, 500))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.connection_info = []
        self.status_text = ""

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
        self.result_tree.setFixedHeight(250)
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
        self.status_info.setFixedHeight(80)
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
        departure = self.departure_input.text().strip()
        destination = self.destination_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")

        if departure and destination:
            self.map_button.setEnabled(True)
            con = Connections(departure, destination, date, time)
            connections_info = con.connection_data_extraction()
            print(connections_info)
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
                self.result_model.clear()
                self.status_text = "No Connection available"
                self.update_status_info()

    def show_connection_info(self, index: QModelIndex):
        selected_row = index.row()
        selected_connection = self.connection_info[selected_row]
        info_window = ConnectionInfoWindow(selected_connection)
        info_window.exec()

    def update_status_info(self):
        self.status_info.setPlainText(self.status_text)

    def get_map(self):
        pass
    """       departure = self.departure_input.text().strip()
        destination = self.destination_input.text().strip()
        cities = [departure, destination]
        cities_coordinates = []
        for city in cities:
            lat, lon = get_coordinates(city)
            if lat and lon:
                cities_coordinates.append({"lat": lat, "lon": lon})
        Map(cities_coordinates)"""


if __name__ == "__main__":
    app = QApplication([])

    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()
