# -*- coding: utf-8 -*-

import sys, os
import serial
import serial.tools.list_ports
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit,
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
import StyleSheets
import resources_rc
import requests
import subprocess
import re


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
            self.data_received.emit(f"Error: {e}")
        finally:
            if hasattr(self, 'ser') and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.running = False
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.cancel_read()
            self.ser.close()
        self.wait()

class UartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.uart_thread = None
        self.web_timer = QTimer(self)
        self.web_timer.timeout.connect(self.fetchDataFromServer)
        self.is_fetching = False

    def initUI(self):
        self.setWindowTitle("SolarTrackerApp")
        self.setWindowIcon(QIcon(':/icon.ico'))
        self.setGeometry(100, 100, 500, 600)
        self.setMinimumSize(500, 600)

        font = QFont()
        font.setPointSize(9)
        QApplication.instance().setFont(font)
        
        # Main layout
        main_layout = QVBoxLayout()

        # Port and BaudRate Section
        portBaudLayout = QGridLayout()

        # Port Section
        self.portLabel = QLabel("Port:")
        self.selectPortBox = QComboBox()
        self.selectPortBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.selectPortBox.setStyleSheet(StyleSheets.selectPortFieldStyle)
        self.refreshPorts()
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setStyleSheet(StyleSheets.portButtonStyle)
        self.refreshButton.clicked.connect(self.refreshPorts)

        portBaudLayout.addWidget(self.portLabel, 0, 0)
        portBaudLayout.addWidget(self.selectPortBox, 0, 1)
        portBaudLayout.addWidget(self.refreshButton, 0, 2)

        # BaudRate Section
        self.baudRateLabel = QLabel("BaudRate:")
        self.baudRateBox = QComboBox()
        self.baudRateBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.baudRateBox.setStyleSheet(StyleSheets.selectPortFieldStyle)
        self.baudRateBox.addItems(["9600", "14400", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.portButton = QPushButton("Connect")
        self.portButton.setStyleSheet(StyleSheets.portButtonStyle)
        self.portButton.setMinimumWidth(QPushButton("Disconnect").sizeHint().width())
        self.portButton.clicked.connect(self.toggleConnection)
        
        portBaudLayout.addWidget(self.baudRateLabel, 1, 0)
        portBaudLayout.addWidget(self.baudRateBox, 1, 1)
        portBaudLayout.addWidget(self.portButton, 1, 2)

        # Web Section
        self.webLabel = QLabel("MAC Address:")
        self.ipBox = QLineEdit()
        self.ipBox.setText("9c-9c-1f-c5-77-d4")
        self.ipBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.ipBox.setStyleSheet(StyleSheets.ipBoxFieldStyle)
        self.fetchButton = QPushButton("Fetch")
        self.fetchButton.setStyleSheet(StyleSheets.portButtonStyle)
        self.fetchButton.clicked.connect(self.fetchWebData)

        portBaudLayout.addWidget(self.webLabel, 2, 0)
        portBaudLayout.addWidget(self.ipBox, 2, 1)
        portBaudLayout.addWidget(self.fetchButton, 2, 2)

        # Adjust column stretch
        portBaudLayout.setColumnStretch(0, 1)
        portBaudLayout.setColumnStretch(1, 5)
        portBaudLayout.setColumnStretch(2, 1)

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
        self.data_grid.addWidget(QLabel("Value"), 0, 1, alignment=Qt.AlignCenter)
        
        self.data_grid.addWidget(QLabel("Position"), 0, 3, alignment=Qt.AlignCenter)
        self.data_grid.addWidget(QLabel("Value"), 0, 4, alignment=Qt.AlignCenter)

        self.sensor_labels = {}
        self.position_labels = {}

        # Sensors
        sensors = ["LG", "PG", "LD", "PD"]
        for i, sensor in enumerate(sensors, start=1):
            sensor_label = QLabel(sensor, alignment=Qt.AlignCenter)
            value_label = QLabel("--", alignment=Qt.AlignCenter)
            value_label.setAlignment(Qt.AlignCenter)
            self.sensor_labels[sensor] = value_label
            self.data_grid.addWidget(sensor_label, i, 0)
            self.data_grid.addWidget(value_label, i, 1)

        # Position
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
        self.messageBox.setStyleSheet(StyleSheets.messageBoxStyle)

        # Main layout section
        main_layout.addLayout(portBaudLayout)
        main_layout.addWidget(separator1)
        main_layout.addLayout(self.data_grid)
        main_layout.addWidget(separator2)
        main_layout.addWidget(QLabel("Info:"))
        main_layout.addWidget(self.messageBox)

        # Central widget section
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
            self.portButton.setText("Connect")
            self.messageBox.clear()
            self.messageBox.append("Disconnected.")
            
            self.baudRateBox.setEnabled(True)
            self.refreshButton.setEnabled(True)
            self.selectPortBox.setEnabled(True)
            self.fetchButton.setEnabled(True)
            self.ipBox.setEnabled(True)
            
        else:
            # Connect
            port = self.selectPortBox.currentText()
            if not port:
                self.messageBox.clear()
                self.messageBox.append(f"Select a port.")
                return
            baudrate = int(self.baudRateBox.currentText())
            self.uart_thread = UartReaderThread(port, baudrate)
            self.uart_thread.data_received.connect(self.handleData)
            self.uart_thread.start()
            self.portButton.setText("Disconnect")
            self.messageBox.clear()
            self.messageBox.append(f"Connected to {port}.")
            
            self.baudRateBox.setEnabled(False)
            self.refreshButton.setEnabled(False)
            self.selectPortBox.setEnabled(False)
            self.fetchButton.setEnabled(False)
            self.ipBox.setEnabled(False)

    def handleData(self, data):
        try:
            json_data = json.loads(data)
            formatted_data = json.dumps(json_data, indent=4)
            self.messageBox.clear()
            self.messageBox.append(f"Received data:\n{formatted_data}")

            # Update sensors and position values
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
            self.messageBox.append(f"{data}")
    
    # Find IP by MAC
    def find_ip_by_mac(self, mac_address):
        try:
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8')
            for line in output.splitlines():
                if mac_address.lower() in line.lower():
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if match:
                        return match.group(1)
            return None
        except Exception as e:
            self.messageBox.append(f"Error finding IP for MAC {mac_address}: {e}")
            return None
    
    # Function periodic fetch data from Server
    def fetchWebData(self):
        if not self.is_fetching:
            self.is_fetching = True
            self.fetchButton.setText("Stop Fetching")
            self.web_timer.start(1000)  # 1 sec
            self.messageBox.append("Started fetching data from server...")
            
            self.selectPortBox.setEnabled(False)
            self.refreshButton.setEnabled(False)
            self.baudRateBox.setEnabled(False)
            self.portButton.setEnabled(False)
            self.ipBox.setEnabled(False)

        else:
            # Stop periodic fetch data
            self.is_fetching = False
            self.fetchButton.setText("Fetch")
            self.web_timer.stop()
            self.messageBox.append("Stopped fetching data from server.")
            
            self.selectPortBox.setEnabled(True)
            self.refreshButton.setEnabled(True)
            self.baudRateBox.setEnabled(True)
            self.portButton.setEnabled(True)
            self.ipBox.setEnabled(True)
            
    # Function fetch data from Server
    def fetchDataFromServer(self):
        mac_address = self.ipBox.text()
        ip_address = self.find_ip_by_mac(mac_address)

        if not ip_address:
            self.messageBox.clear()
            self.messageBox.append(f"Could not find IP for MAC {mac_address}")
            return

        url = f"http://{ip_address}/data"

        try:
            response = requests.get(url, timeout=1)
            response.raise_for_status()
            json_data = response.json()
            formatted_data = json.dumps(json_data, indent=4)
            self.messageBox.clear()
            self.messageBox.append(f"Received data from {ip_address}:\n{formatted_data}")

            # Update sensors and position values
            sensors = json_data.get("sensors", {})
            position = json_data.get("position", {})

            for sensor, value in sensors.items():
                if sensor in self.sensor_labels:
                    self.sensor_labels[sensor].setText(str(value))

            for pos, value in position.items():
                if pos in self.position_labels:
                    self.position_labels[pos].setText(str(value))

        except requests.exceptions.RequestException as e:
            self.messageBox.clear()
            self.messageBox.append(f"{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UartApp()
    window.show()
    sys.exit(app.exec_())