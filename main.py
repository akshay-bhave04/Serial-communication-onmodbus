import time
import json
import logging
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configure logging for clean error messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
SERIAL_PORT = '/tmp/ttyS1'  # Replace with your client-side virtual port
BAUDRATE = 9600
SLAVE_ID = 1
POLL_INTERVAL = 3     # Seconds between polls

def process_payload(registers):
   
    # Unpack raw registers
    raw_voltage = registers[0] # 40001
    raw_current = registers[1] # 40002
    raw_power = registers[2]   # 40003
    raw_energy = registers[3]  # 40004

    # Handle Signed 16-bit integer for Current
    # If the 16th bit is set (value > 32767), it's a negative number in two's complement
    if raw_current > 32767:
        raw_current -= 65536

    # Apply scaling factors (0.1) and format data
    data = {
        "system_voltage_V": raw_voltage * 0.1,
        "system_current_A": raw_current * 0.1,
        "active_power_kW": raw_power * 0.1,
        "daily_energy_yield_kWh": raw_energy * 0.1
    }
    return data

def main():
    logger.info(f"Initializing Modbus RTU Client on {SERIAL_PORT}...")
    client = ModbusSerialClient(port=SERIAL_PORT, baudrate=BAUDRATE, timeout=1)

    while True:
        try:
            # Reconnect if the connection was lost
            if not client.is_socket_open():
                client.connect()

            # Read 4 Holding Registers. 
            # Note: Modbus addresses are typically 0-indexed, so 40001 corresponds to address 0.
            result = client.read_holding_registers(address=0, count=4, slave=SLAVE_ID)

            if result.isError():
                logger.error(f"Modbus Error: Received error response from slave: {result}")
            else:
                # Structure and print the clean JSON object
                parsed_data = process_payload(result.registers)
                json_payload = json.dumps(parsed_data, indent=4)
                logger.info(f"Payload ready for cloud ingestion:\n{json_payload}")

        # Catch PyModbus specific exceptions (e.g., timeout, connection lost)
        except ModbusException as me:
            logger.error(f"Communication Fault: {me}. Retrying in {POLL_INTERVAL}s...")
            client.close() # Force close to reset state on next loop
            
        # Catch any other unexpected crashes
        except Exception as e:
            logger.error(f"Unexpected System Error: {e}. Retrying in {POLL_INTERVAL}s...")
            client.close()

        finally:
            time.sleep(POLL_INTERVAL)
if __name__ == "__main__":
    main()
