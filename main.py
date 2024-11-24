# -*- coding: utf-8 -*-

import sys, os
import serial
import serial.tools.list_ports
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import StyleSheets
import resources_rc


class UartReaderThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            while self.running:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode('utf-8').strip()
                    self.data_received.emit(data)
        except Exception as e:
            self.data_received.emit(f"Błąd: {e}")
        finally:
            if hasattr(self, 'ser') and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.running = False
        self.wait()


class UartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.uart_thread = None

    def initUI(self):
        self.setWindowTitle("SolarTrackerApp")
        # base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        # icon_path = os.path.join(base_path, 'icon.ico')
        # self.setWindowIcon(QIcon(icon_path))
        self.setWindowIcon(QIcon(':/icon.ico'))
        self.setGeometry(100, 100, 500, 500)

        font = QFont()
        font.setPointSize(9)
        QApplication.instance().setFont(font)
        
        # Main layout
        main_layout = QVBoxLayout()

        # Port Section
        selectPortLine = QHBoxLayout()
        self.portLabel = QLabel("Port:")
        self.selectPortBox = QComboBox()
        self.selectPortBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.selectPortBox.setStyleSheet(StyleSheets.selectPortFieldStyle)
        self.refreshPorts()
        self.portButton = QPushButton("Połącz")
        self.portButton.setStyleSheet(StyleSheets.portButtonStyle)
        self.portButton.clicked.connect(self.toggleConnection)

        selectPortLine.addWidget(self.portLabel)
        selectPortLine.addWidget(self.selectPortBox)
        selectPortLine.addWidget(self.portButton)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)


        # Received Data Section
        self.data_grid = QGridLayout()
        self.data_grid.addWidget(QLabel("Sensor"), 0, 0, alignment=Qt.AlignCenter)
        self.data_grid.addWidget(QLabel("Wartość"), 0, 1, alignment=Qt.AlignCenter)
        
        self.data_grid.addWidget(QLabel("Położenie"), 0, 3, alignment=Qt.AlignCenter)
        self.data_grid.addWidget(QLabel("Wartość"), 0, 4, alignment=Qt.AlignCenter)

        self.sensor_labels = {}
        self.position_labels = {}

        # Sensory
        sensors = ["LG", "PG", "LD", "PD"]
        for i, sensor in enumerate(sensors, start=1):
            sensor_label = QLabel(sensor, alignment=Qt.AlignCenter)
            value_label = QLabel("--", alignment=Qt.AlignCenter)
            value_label.setAlignment(Qt.AlignCenter)
            self.sensor_labels[sensor] = value_label
            self.data_grid.addWidget(sensor_label, i, 0)
            self.data_grid.addWidget(value_label, i, 1)

        # Pozycje
        positions = ["X", "Y"]
        for i, pos in enumerate(positions, start=1):
            position_label = QLabel(pos, alignment=Qt.AlignCenter)
            value_label = QLabel("--", alignment=Qt.AlignCenter)
            self.position_labels[pos] = value_label
            self.data_grid.addWidget(position_label, i, 3)
            self.data_grid.addWidget(value_label, i, 4)

        separator_vertical = QFrame()
        separator_vertical.setFrameShape(QFrame.VLine)
        separator_vertical.setFrameShadow(QFrame.Sunken)
        self.data_grid.addWidget(separator_vertical, 0, 2, len(sensors) + len(positions), 1)

        # Message Box
        self.messageBox = QTextEdit()
        self.messageBox.setReadOnly(True)
        # self.messageBox.setMaximumHeight(60)
        self.messageBox.setStyleSheet(StyleSheets.messageBoxStyle)

        # Dodanie sekcji do głównego layoutu
        main_layout.addLayout(selectPortLine)
        main_layout.addWidget(separator1)
        main_layout.addLayout(self.data_grid)
        main_layout.addWidget(separator2)
        main_layout.addWidget(QLabel("Info:"))
        main_layout.addWidget(self.messageBox)

        # Ustawienie centralnego widgetu
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def refreshPorts(self):
        self.selectPortBox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.selectPortBox.addItem(port.device)

    def toggleConnection(self):
        if self.uart_thread and self.uart_thread.isRunning():
            # Disconnect
            self.uart_thread.stop()
            self.uart_thread = None
            self.portButton.setText("Połącz")
            self.messageBox.clear()
            self.messageBox.append("Rozłączono.")
        else:
            # Connect
            port = self.selectPortBox.currentText()
            if not port:
                self.messageBox.clear()
                self.messageBox.append(f"Wybierz port.")
                return
            baudrate = 9600  # Można dodać możliwość wyboru
            self.uart_thread = UartReaderThread(port, baudrate)
            self.uart_thread.data_received.connect(self.handleData)
            self.uart_thread.start()
            self.portButton.setText("Rozłącz")
            self.messageBox.clear()
            self.messageBox.append(f"Połączono z {port}.")

    def handleData(self, data):
        try:
            json_data = json.loads(data)
            formatted_data = json.dumps(json_data, indent=4)
            self.messageBox.clear()
            self.messageBox.append(f"Odebrano dane:\n{formatted_data}")

            # Aktualizacja pól dla sensorów
            sensors = json_data.get("sensors", {})
            position = json_data.get("position", {})

            for sensor, value in sensors.items():
                if sensor in self.sensor_labels:
                    self.sensor_labels[sensor].setText(str(value))

            for pos, value in position.items():
                if pos in self.position_labels:
                    self.position_labels[pos].setText(str(value))

        except json.JSONDecodeError:
            self.messageBox.clear()
            self.messageBox.append(f"Nieprawidłowy JSON: {data}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UartApp()
    window.show()
    sys.exit(app.exec_())