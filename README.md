# Solar Inverter Modbus RTU Simulator

A fault-tolerant Modbus RTU client-server environment designed to simulate data polling from a solar inverter. This project was developed as part of a protocol challenge to handle real-world communication constraints.

##  Features
- **Mock Serial Port:** Uses virtual serial ports to simulate hardware communication.
- **Modbus RTU Protocol:** Implements both client and server using `pymodbus`.
- **Fault Tolerance:** Robust error handling for intermittent connection issues.
- **Real-time Polling:** Automated data collection from simulated inverter registers.

##  Tech Stack
- Language: Python 3.x
- Libraries: `pymodbus`, `pyserial`
- Environment: Linux (Ubuntu 22.04) / Windows 11
- Tools: `socat` (for virtual serial port bridging on Linux)

##  How to Run
1. **Setup Virtual Serial Ports:**
   **Example for Linux**
   bash
   socat -d -d PTY,link=/tmp/ttyS0,raw,echo=0 PTY,link=/tmp/ttyS1,raw,echo=0
2. **Install Dependencies:**
   bash
   pip install pymodbus pyserial
   
3. **Start the Server (Simulator):**
   bash
   python server.py
   
4. **Run the Client (Data Collector):**
   bash
   python main.py
   

##  Project Goals
The main objective was to create a reliable system that can fetch data from industrial hardware (Solar Inverters) without needing the physical device present during the initial development phase.
