# SolarTracker App
This application allows the user to connect to the Solar Tracker via UART transmission and read sensor and control readings.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [How to Use](#how-to-use)
5. [Author](#author)
6. [License](#license)

## Introduction
The SolarTracker App is a Python-based graphical user interface (GUI) application designed to interact with a solar tracking system. It enables users to connect to the tracker via UART communication, monitor sensor data, and control system parameters in real time. The application leverages PyQt5 for its user-friendly interface and pyserial for UART communication.

## Installation
Steganography App requires Python and the PyQt5 library. To install the necessary dependencies, follow these steps:

1. Clone the repository to your local machine:

```bash
git clone https://github.com/BrzozkaMarcin/SteganographyApp
```

2. Navigate to the project directory:
```bash
cd SolarTrackerApp
```

3. Install the required libraries using pip:
```bash
pip install -r requirements.txt
```

4. Build resource file using pyrcc5:
```bash
pyrcc5 resources.qrc -o resources_rc.py
```

## Usage
To run the application follow these steps:

1. Navigate to the project directory:
```bash
cd SolarTrackerApp
```

2. Run the `main.py` file:
```bash
python main.py
```

## How to Use
1. **Connect the Hardware:**
   - Ensure that the Solar Tracker hardware is properly connected to your computer via a UART-compatible serial port.

2. **Launch the Application:**
   - Follow the steps in the [Usage](#usage) section to start the application.

3. **Select a Serial Port:**
   - From the drop-down menu in the application, choose the appropriate serial port and baud rate for your Solar Tracker.

4. **Establish the Connection:**
   - Click the "Connect" button to establish communication with the Solar Tracker.

5. **Monitor Data:**
   - View live sensor readings and system control parameters in the GUI.

6. **Disconnect:**
   - After completing your session, click the "Disconnect" button to safely terminate the connection.

## Author
SolarTracker App was created, maintained, and developed by Marcin Brzózka.

## License
This project is licensed under the MIT. For more information, see the LICENSE file.
