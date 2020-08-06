```console

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
MicroPython library which provides easy connectivity to [WolkAbout IoT Platform](https://demo.wolkabout.com/#/login).

Supported device communication protocol(s):
- WolkAbout Protocol

## Requirements

WolkConnect-MicroPython depends on an implementation of an MQTT client. This dependency can be satisfied by using MicroPython's [umqtt.simple](https://github.com/micropython/micropython-lib/tree/master/umqtt.simple). Alternatively, use [umqtt.robust](https://github.com/micropython/micropython-lib/tree/master/umqtt.robust) or Pycom's [mqtt](https://github.com/pycom/pycom-libraries/blob/master/lib/mqtt/mqtt.py).

## Installation

 - Clone this repository:
```console
git clone https://github.com/Wolkabout/WolkConnect-MicroPython.git
```
 - Copy ``wolk.py`` into the *lib* directory of your board.

## Example Usage

### Establishing connection with WolkAbout IoT Platform

Create a device on WolkAbout IoT platform by using the provided `Simple example` device type.  
This device type fits [main.py](https://github.com/Wolkabout/WolkConnect-MicroPython/blob/master/examples/simple/main.py) and demonstrates the sending of a temperature sensor reading.

```python
from [mqtt] import MQTTClient
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
