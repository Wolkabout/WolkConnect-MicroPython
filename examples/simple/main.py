from machine import unique_id
from time import sleep
from ubinascii import hexlify
import network
from urandom import getrandbits
from sys import print_exception


from umqtt.simple import MQTTClient
import wolk


CLIENT_ID = hexlify(unique_id())
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_pasword"

WIFI_SSID = "WIFI_SSID"
WIFI_PASSWORD = "WIFI_PASSWORD"

WLAN = network.WLAN(network.STA_IF)
WLAN.active(True)
if not WLAN.isconnected():
    print("connecting to network...")
    WLAN.connect(WIFI_SSID, WIFI_PASSWORD)
    while not WLAN.isconnected():
        pass
print("network config:", WLAN.ifconfig())

MQTT_CLIENT = MQTTClient(
    CLIENT_ID, wolk.HOST, wolk.PORT, wolk.DEVICE_KEY, wolk.DEVICE_PASSWORD
)

WOLK_DEVICE = wolk.WolkConnect(MQTT_CLIENT)

try:
    WOLK_DEVICE.connect()

    while True:
        WOLK_DEVICE.add_sensor_reading("T", getrandbits(6))
        WOLK_DEVICE.publish()
        sleep(5)
except Exception as e:
    sys.print_exception(e)
    WOLK_DEVICE.disconnect()