import time
import random
import threading
import logging
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger()

def update_registers(context):
    """
    This function runs in a background thread. It generates random, realistic 
    inverter data and updates the Modbus holding registers every 2 seconds.
    """
    # In PyModbus, when single=True, the slave context is accessed via index 0
    slave_context = context[0]
    
    # Function code 3 represents the Holding Registers block
    register_block = 3 
    starting_address = 0

    while True:
        # 1. Generate realistic fluctuating data
        voltage = random.randint(2250, 2350)  # 225.0V to 235.0V
        power = random.randint(20, 50)        # 2.0kW to 5.0kW
        energy = random.randint(1500, 1510)   # 150.0kWh to 151.0kWh
        
        # Simulate Current fluctuating between -50 (-5.0A) and 150 (15.0A)
        # Negative current means charging. We must convert negative numbers 
        # to a 16-bit two's complement integer for Modbus transmission.
        raw_current = random.randint(-50, 150)
        if raw_current < 0:
            current = 65536 + raw_current # Two's complement conversion
        else:
            current = raw_current

        # 2. Package the values
        new_values = [voltage, current, power, energy]

        # 3. Inject the new values into the Modbus Server's memory
        slave_context.setValues(register_block, starting_address, new_values)
        
        log.info(f"Updated Registers internally: Voltage={voltage/10}V, Current={raw_current/10}A")
        
        # Wait 2 seconds before fluctuating again
        time.sleep(2)

def run_live_mock_inverter():
    # Initialize registers with zeros
    store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0, 0, 0, 0]))
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Synapse Challenge'
    identity.ModelName = 'Live Mock Inverter'

    # Start the background thread to update values
    update_thread = threading.Thread(target=update_registers, args=(context,), daemon=True)
    update_thread.start()

    print("Starting LIVE Mock Modbus Server on /tmp/ttyS0...")
    
    # Start the Modbus Server (this blocks the main thread, which is why we needed the background thread above)
    StartSerialServer(
        context=context, 
        identity=identity, 
        port='/tmp/ttyS0', # Must match one end of your socat cable
        baudrate=9600
    )
if __name__ == "__main__":
    run_live_mock_inverter()
