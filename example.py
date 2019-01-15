import machine
import time
import ubinascii
import urandom
import sys


from umqtt.simple import MQTTClient
from wolk import wolk


client_id = ubinascii.hexlify(machine.unique_id())
wolk.HOST = "api-demo.wolkabout.com"
wolk.DEVICE_KEY = "some_key"
wolk.DEVICE_PASSWORD = "device_password"
wolk.ACTUATOR_REFERENCES = None


mqtt_client = MQTTClient(
    client_id, wolk.HOST, wolk.PORT, wolk.DEVICE_KEY, wolk.DEVICE_PASSWORD
)


wolk_device = wolk.WolkConnect(
    mqtt_client=mqtt_client,
    actuation_handler=None,
    actuator_status_provider=None,
    configuration_handler=None,
    configuration_provider=None,
)

try:
    wolk_device.connect()
    while True:
        wolk_device.add_sensor_reading("T", urandom.getrandbits(6))
        wolk_device.publish()
        time.sleep(5)
except Exception as e:
    sys.print_exception(e)
    wolk_device.disconnect()
