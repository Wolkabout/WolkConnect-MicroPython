"""Connect to WolkAbout IoT Platform and periodically send a sensor reading."""
#   Copyright 2020 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from sys import print_exception
from time import sleep
import network
from machine import unique_id
from ubinascii import hexlify
from urandom import getrandbits

# External modules that need to be placed under /flash/lib
from umqtt.simple import MQTTClient
import wolk


# WolkAbout
CLIENT_ID = hexlify(unique_id())
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_password"

wolk.HOST = "api-demo.wolkabout.com"
wolk.PORT = 1883

# WiFi
WIFI_SSID = "WIFI_SSID"
WIFI_PASSWORD = "WIFI_PASSWORD"

WLAN = network.WLAN(network.STA_IF)
WLAN.active(True)
if not WLAN.isconnected():
    print("connecting to network {}...".format(WIFI_SSID))
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
        temperature = getrandbits(6)
        WOLK_DEVICE.add_sensor_reading("T", temperature)
        print("Publishing temperature reading: " + str(temperature))
        WOLK_DEVICE.publish()
        sleep(5)
except Exception as e:
    print_exception(e)
    WOLK_DEVICE.disconnect()
