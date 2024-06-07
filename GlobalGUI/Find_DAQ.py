import nidaqmx

# List all available DAQ devices
system = nidaqmx.system.System.local()
devices = system.devices

# Iterate through the devices and print their information
for device in devices:
    print(f"Device Name: {device.name}")




# Specify the name of the DAC channel you want to read from
channel_name = "Dev2/ai0"  # Replace with the actual channel name

# Create a task for reading from the DAC channel
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(channel_name)
    
    # Read one value from the DAC channel
    value = task.read()
    
# Print the read value
print(f"Value read from {channel_name}: {value}")