# WolkConnect-MicroPython
```sh

██╗    ██╗ ██████╗ ██╗     ██╗  ██╗ ██████╗ ██████╗ ███╗   ██╗███╗   ██╗███████╗ ██████╗████████╗
██║    ██║██╔═══██╗██║     ██║ ██╔╝██╔════╝██╔═══██╗████╗  ██║████╗  ██║██╔════╝██╔════╝╚══██╔══╝
██║ █╗ ██║██║   ██║██║     █████╔╝ ██║     ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║        ██║   
██║███╗██║██║   ██║██║     ██╔═██╗ ██║     ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║        ██║   
╚███╔███╔╝╚██████╔╝███████╗██║  ██╗╚██████╗╚██████╔╝██║ ╚████║██║ ╚████║███████╗╚██████╗   ██║   
 ╚══╝╚══╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝ ╚═════╝   ╚═╝   
                                                                                                 
███╗   ███╗██╗ ██████╗██████╗  ██████╗ ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗     
████╗ ████║██║██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║     
██╔████╔██║██║██║     ██████╔╝██║   ██║██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║     
██║╚██╔╝██║██║██║     ██╔══██╗██║   ██║██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║     
██║ ╚═╝ ██║██║╚██████╗██║  ██║╚██████╔╝██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║     
╚═╝     ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝     
                                                                                                 

```
MicroPython library which provides easy connectivity to[WolkAbout IoT Platform](https://demo.wolkabout.com/#/login).

Supported device communication protocol(s):
- JsonSingleReferenceProtocol

## Requirements

WolkConnect-MicroPython depends on an implementation of an MQTT client. This dependency can be satisfied by using MicroPython's [umqtt.simple](https://github.com/micropython/micropython-lib/tree/master/umqtt.simple) or [umqtt.robust](https://github.com/micropython/micropython-lib/tree/master/umqtt.robust). Alternatively, use Pycom's [mqtt module](https://github.com/pycom/pycom-libraries/blob/master/lib/mqtt/mqtt.py).

## Installation

Clone this repository and then copy *wolk.py* into the *lib* directory of your board.

## Example Usage

### Establishing connection with WolkAbout IoT Platform
```python
from [mqtt module] import MQTTClient
import wolk

CLIENT_ID = hexlify(unique_id())
# Setup the device credentials which you received
# when the device was created on the platform
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_password"

# WiFi connection is required before this step

MQTT_CLIENT = MQTTClient(
    CLIENT_ID, wolk.HOST, wolk.PORT, wolk.DEVICE_KEY, wolk.DEVICE_PASSWORD
)

WOLK_DEVICE = wolk.WolkConnect(MQTT_CLIENT)

WOLK_DEVICE.connect()
```

### Adding sensor readings
```python
WOLK_DEVICE.add_sensor_reading("T", 21.17)
```

### Adding events
```python
# Alarm active
WOLK_DEVICE.add_alarm("HH", True)
# Alarm not active
WOLK_DEVICE.add_alarm("HH", False)
```

### Data publish strategy
By default, 20 readings are stored in memory but this can be changed by specifying a different number when creating an instance of WolkConnect like so:

```python
WOLK_DEVICE = wolk.WolkConnect(MQTT_CLIENT, storage_size=50)
```

Stored sensor readings and alarms are pushed to WolkAbout IoT Platform on demand by calling:

```python
WOLK_DEVICE.publish()
```

### Disconnecting from the platform
```python
WOLK_DEVICE.disconnect()
```

### Actuators
In order to control the state of actuators connected to the device, the user must implement an actuation handler function and an actuator status provider function.
A list of actuator references must also be provided when creating a connection to WolkAbout IoT Platform to be able to receive incoming commands. See function docs in *wolk.py* for implementation guidelines.  

```python
CLIENT_ID = hexlify(unique_id())
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_password"
wolk.ACTUATOR_REFERENCES = ["SW"]

LIGHT_SWITCH = Pin("P3", mode=Pin.OUT)
LIGHT_SWITCH.value(False)

def get_actuator_status(reference):
    if reference == "SW":
        return wolk.ACTUATOR_STATE_READY, LIGHT_SWITCH.value()


def handle_actuation(reference, value):
    if reference == "SW":
        if value is True:
            LIGHT_SWITCH.value(True)
        else:
            LIGHT_SWITCH.value(False)


MQTT_CLIENT = MQTTClient(
    CLIENT_ID, wolk.HOST, wolk.PORT, wolk.DEVICE_KEY, wolk.DEVICE_PASSWORD
)

WOLK_DEVICE = wolk.WolkConnect(MQTT_CLIENT, handle_actuation, get_actuator_status)

WOLK_DEVICE.connect()

#Publish current actuator status identified by reference
WOLK_DEVICE.publish_actuator_status("SW")
```

### Device configuration options
Similarly to actuators, configuration options depend on an implementation of a configuration provider and a configuration handler.
Implementation guidelines can be seen in function docs in *wolk.py*.

```python

def configuration_provider():
	configurations = dict()
	configurations["config_1"] = "some value"
	configurations["config_2"] = False
	return configurations

def configuration_handler(configurations):
	for reference, values in configurations.items():
		if reference == "config_1":
			# handle setting of the value
			pass
		if reference == "config_2":
			pass


# Pass these functions to WolkConnect

WOLK_DEVICE = wolk.WolkConnect(
		MQTTClient,
		configuration_handler=configuration_handler,
		configuration_provider=configuration_provider
    )

WOLK_DEVICE.connect()
# Publish all device's configuration options
WOLK_DEVICE.publish_configuration()
```

### Keep alive
When you want your device to stay connected and you are not sending anything to the platform, a keep alive message should be sent periodically, say every 5 minutes, with:
```python
WOLK_DEVICE.send_ping()
```

### Device firmware update
This feature was not implemented in this WolkConnect library due to eventual hardware constrains.
