import requests
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QTextEdit

from modules import connection, location


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.connections = None
        self.setWindowTitle("Transport Search")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        form_layout = QHBoxLayout()
        layout.addLayout(form_layout)

        from_label = QLabel("From:")
        self.from_input = QLineEdit()
        form_layout.addWidget(from_label)
        form_layout.addWidget(self.from_input)

        to_label = QLabel("To:")
        self.to_input = QLineEdit()
        form_layout.addWidget(to_label)
        form_layout.addWidget(self.to_input)

        via_label = QLabel("Via:")
        self.via_input = QLineEdit()
        form_layout.addWidget(via_label)
        form_layout.addWidget(self.via_input)

        datetime_label = QLabel("Date and time (optional):")
        self.datetime_input = QLineEdit()
        form_layout.addWidget(datetime_label)
        form_layout.addWidget(self.datetime_input)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_connections)
        layout.addWidget(search_button)

        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

    def fetch(self, url, params=None):
        response = requests.get(url, params=params)
        if response.status_code != 200:
            exit(f"Error from API: {response.status_code}")
        return response.json()

    def search_connections(self):
        from_station = self.from_input.text()
        to_station = self.to_input.text()
        via_station = self.via_input.text()
        date_time = self.datetime_input.text()

        search = from_station and to_station
        if search:
            params = {
                'from': from_station,
                'to': to_station,
                'limit': 6,
            }

            if date_time:
                date_time_obj = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
                params['date'] = date_time_obj.strftime('%Y-%m-%d')
                params['time'] = date_time_obj.strftime('%H:%M')

            if via_station:
                params['via'] = via_station

            response = self.fetch('https://transport.opendata.ch/v1/connections', params=params)

            from_station = response.get('from', {}).get('name', '')
            to_station = response.get('to', {}).get('name', '')

            stations_from = []
            stations_to = []

            if 'stations' in response:
                if response['stations'].get('from'):
                    for station in response['stations']['from'][1:4]:
                        if station.get('score') and station['score'] > 97:
                            stations_from.append(station['name'])

                if response['stations'].get('to'):
                    for station in response['stations']['to'][1:4]:
                        if station.get('score') and station['score'] > 97:
                            stations_to.append(station['name'])

            result = f'From: {from_station}\nTo: {to_station}\nStations from: {", ".join(stations_from)}\nStations to: {", ".join(stations_to)}'
            self.result_text.setPlainText(result)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
