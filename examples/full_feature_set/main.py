"""Connect to WolkAbout IoT Platform and periodically send sensor data."""
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
from machine import unique_id
from time import sleep
from ubinascii import hexlify
import network
from urandom import getrandbits
from sys import print_exception

# External modules that need to be placed under /flash/lib
from umqtt.simple import MQTTClient
import wolk

# WolkAbout
CLIENT_ID = hexlify(unique_id())
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_password"
wolk.ACTUATOR_REFERENCES = ["SW", "SL"]

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

# Device actuators
SWITCH = False
SLIDER = 0


def get_actuator_status(reference):
    if reference == "SW":
        return wolk.ACTUATOR_STATE_READY, SWITCH
    if reference == "SL":
        return wolk.ACTUATOR_STATE_READY, SLIDER


def handle_actuation(reference, value):
    global SWITCH
    global SLIDER
    print("Setting reference {} to value {}".format(reference, value))
    if reference == "SW":
        SWITCH = value
        return
    if reference == "SL":
        SLIDER = value


# Device configuration
HEART_BEAT = 5
LOG_LEVEL = "info"
ENABLED_FEEDS = ["T", "P", "H", "ACL"]


def get_configuration():
    formatted = ",".join(ENABLED_FEEDS)

    return {"HB": HEART_BEAT, "LL": LOG_LEVEL, "EF": formatted}


def handle_configuration(configuration):
    global HEART_BEAT
    global LOG_LEVEL
    global ENABLED_FEEDS

    for reference, value in configuration.items():
        print("Setting reference {} to value {}".format(reference, value))
        if reference == "LL":
            LOG_LEVEL = value
            continue

        if reference == "HB":
            HEART_BEAT = value
            continue

        if reference == "EF":
            ENABLED_FEEDS = value.split(",")


def randint(min, max):
    span = max - min + 1
    div = 0x3fffffff // span
    offset = getrandbits(30) // div
    val = min + offset
    return val


WOLK_DEVICE = wolk.WolkConnect(
    MQTT_CLIENT,
    handle_actuation,
    get_actuator_status,
    handle_configuration,
    get_configuration,
)


try:
    WOLK_DEVICE.connect()
    WOLK_DEVICE.publish_configuration()
    WOLK_DEVICE.publish_actuator_status("SW")
    WOLK_DEVICE.publish_actuator_status("SL")

    while True:
        try:
            MQTT_CLIENT.check_msg()
        except OSError as os_e:
            # sometimes an 'empty socket read' error happens
            # and that needlessly kills the script
            pass
        if "T" in ENABLED_FEEDS:
            temperature = randint(10, 25)
            WOLK_DEVICE.add_sensor_reading("T", temperature)
        if "P" in ENABLED_FEEDS:
            pressure = randint(990, 1010)
            WOLK_DEVICE.add_sensor_reading("P", pressure)
        if "H" in ENABLED_FEEDS:
            humidity = randint(0, 100)
            WOLK_DEVICE.add_sensor_reading("H", humidity)
            if humidity > 80:
                WOLK_DEVICE.add_alarm("HH", True)
            else:
                WOLK_DEVICE.add_alarm("HH", False)
        if "ACL" in ENABLED_FEEDS:
            accelerometer = (randint(0, 5), randint(0, 5), randint(0, 5))
            WOLK_DEVICE.add_sensor_reading("ACL", accelerometer)

        WOLK_DEVICE.publish()
        sleep(HEART_BEAT)
except Exception as e:
    print_exception(e)
    WOLK_DEVICE.disconnect()
