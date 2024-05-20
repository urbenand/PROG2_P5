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
from PySide6.QtCore import QSize, QDate, QTime, QModelIndex, Qt
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

        for section in connection_info.get("sections", []):
            journey = section.get("journey", {})
            departure_info = section.get("departure", {})
            arrival_info = section.get("arrival", {})

            if journey:
                journey_item = QStandardItem(
                    f"{journey.get('category', 'N/A')} {journey.get('number', 'N/A')}\n"
                    f"Direction: {journey.get('to', 'N/A')}"
                )
            else:
                journey_item = QStandardItem(
                    f"Walk Duration:\n{int(section.get('walk_duration') / 60)} minutes"
                )
            departure_item = QStandardItem(
                f"{departure_info.get('station_name', 'N/A')}\n"
                f"{departure_info.get('departure', 'N/A').split(' ')[1] if 'departure' in departure_info else 'N/A'}"
            )
            arrival_item = QStandardItem(
                f"{arrival_info.get('station_name', 'N/A')}\n"
                f"{arrival_info.get('arrival', 'N/A').split(' ')[1] if 'arrival' in arrival_info else 'N/A'}"
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
        self.result_model = QStandardItemModel()
        self.result_model.setHorizontalHeaderLabels(["Information", "Departure", "Arrival", "Duration", "Transfers"])
        self.result_tree.setModel(self.result_model)
        self.result_tree.clicked.connect(self.show_connection_info)
        layout.addWidget(self.result_tree)

        self.result_tree.setColumnWidth(0, 220)
        self.result_tree.setColumnWidth(1, 120)
        self.result_tree.setColumnWidth(2, 120)
        self.result_tree.setColumnWidth(3, 80)
        self.result_tree.setColumnWidth(4, 60)

        status_label = QLabel("Status Information")
        layout.addWidget(status_label)

        self.status_info = QTextEdit()
        self.status_info.setReadOnly(True)
        self.status_info.setFixedHeight(50)
        layout.addWidget(self.status_info)

        self.map_view = QLabel("MAP HERE")
        self.map_view.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.map_view)

        self.update_status_info()

    def check_input_fields(self):
        if self.departure_input.text().strip() and self.destination_input.text().strip():
            self.search_button.setEnabled(True)
        else:
            self.search_button.setEnabled(False)

    def search_connections(self):
        departure = self.departure_input.text().strip()
        destination = self.destination_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")
        if departure and destination:
            con = Connections(departure, destination, date, time)
            connections_info = con.connection_data_extraction()
            self.connection_info = connections_info
            self.result_model.removeRows(0, self.result_model.rowCount())
            print(connections_info)
            if connections_info:
                for connection in connections_info:
                    products = connection.get("products", [])
                    products_numbers = ", ".join(products)
                    connection_item = QStandardItem(
                        f"{products_numbers}"
                        f" - To {connection['to']['name']}")
                    self.result_model.appendRow(connection_item)
                    self.result_model.setItem(connection_item.row(), 1,
                                              QStandardItem(connection["from"]["departure"]))
                    self.result_model.setItem(connection_item.row(), 2,
                                              QStandardItem(connection["to"]["arrival"]))
                    self.result_model.setItem(connection_item.row(), 3,
                                              QStandardItem(connection["duration"]))
                    self.result_model.setItem(connection_item.row(), 4, QStandardItem(str(connection["transfers"])))
            else:
                self.result_model.clear()

    def show_connection_info(self, index: QModelIndex):
        selected_row = index.row()
        selected_connection = self.connection_info[selected_row]
        info_window = ConnectionInfoWindow(selected_connection)
        info_window.exec()

    def update_status_info(self, status_text="BRB"):
        self.status_info.setPlainText(status_text)


if __name__ == "__main__":
    app = QApplication([])

    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()
