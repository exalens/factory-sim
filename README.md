# Factory Simulator
# A simple OPC-UA Factory Process simulator for testing Process Endpoint Monitoring

The process simulates a Bakery production line with systems such as an industrial robot with an accurate kinematic representation of its
pick and place position (X, Y, Z coordinations) in the process, as well as other PLC simulated process states, I/O and recipe process variables.
The OPC-UA server simulates the collection process endpoint data from a SCADA system that is aggregating data acquisition from multiple OT device endpoints.

# To activate the OPC-UA Simulator ensure all Python requirements are installed, and run:

<code>python3 opc-ua/baking/factory.py</code>

This will execute the OPC-UA server that publishes data from Baking production line pick and place simulation on the IP of the current host (e.g., 0.0.0.0).

# To activate the simulator production process, run: 

<code>python3 opc-ua/baking/client.py</code>

A menu will appear to allow you to set the state of the process from idle (False) to active (True), change the process recipe, and inject anomalies into 
the process. Note that client.py can connect remotely to factory.py OPC-UA server to change the process state, but anomaly injection requires that it is running on the same host.

You can use any OPC-UA client to connect to the OPC-UA server (no authentication is required) and start reading legitimate and anomalous process data generated by the simulation.
