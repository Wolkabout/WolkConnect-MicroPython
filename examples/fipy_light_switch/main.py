from sys import print_exception
from time import sleep
from time import sleep_ms

import pycom
from crypto import getrandbits
from machine import Pin
from machine import Timer
from machine import unique_id
from mqtt import MQTTClient
from network import WLAN
from ubinascii import hexlify

import wolk

# External modules that need to be placed under /flash/lib

# WolkAbout
CLIENT_ID = hexlify(unique_id())
wolk.HOST = "api-demo.wolkabout.com"
wolk.PORT = 1883
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_password"
wolk.ACTUATOR_REFERENCES = ["SW"]

# WiFi
WIFI_SSID = "WIFI_SSID"
WIFI_AUTH = WLAN.WPA2  # WEP, WPA, WPA2, WPA2_ENT
WIFI_PASSWORD = "WIFI_PASSWORD"

# Relay Click connected on P3 (GPIO4)
LIGHT_SWITCH = Pin("P3", mode=Pin.OUT)
LIGHT_SWITCH.value(False)
# Set onboard LED to dim red
pycom.heartbeat(False)
pycom.rgbled(0x100000)


def get_actuator_status(reference):
    if reference == "SW":
        return wolk.ACTUATOR_STATE_READY, LIGHT_SWITCH.value()


def handle_actuation(reference, value):
    if reference == "SW":
        if value is True:
            LIGHT_SWITCH.value(True)
            pycom.rgbled(0x001000)
        else:
            LIGHT_SWITCH.value(False)
            pycom.rgbled(0x100000)


# WIFI setup
wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, auth=(WIFI_AUTH, WIFI_PASSWORD), timeout=5000)
sleep(2)  # wlan.isconnected can return a false positve so best to wait a bit
while not wlan.isconnected():
    machine.idle()
print("network configuration:", wlan.ifconfig())


# WolkAbout setup
MQTT_CLIENT = MQTTClient(
    CLIENT_ID, wolk.HOST, wolk.PORT, wolk.DEVICE_KEY, wolk.DEVICE_PASSWORD
)

WOLK_DEVICE = wolk.WolkConnect(
    MQTT_CLIENT, handle_actuation, get_actuator_status
)

SLEEP_INTERVAL_MS = 20

try:
    WOLK_DEVICE.connect()
    WOLK_DEVICE.publish_actuator_status("SW")
    LOOP_COUNTER = 0
    while True:
        LOOP_COUNTER += 1
        try:
            MQTT_CLIENT.check_msg()
        except OSError as os_e:
            # sometimes an 'empty socket read' error happens
            # and that needlessly kills the script
            pass
        if LOOP_COUNTER % 3000 == 0:  # every 60 seconds
            WOLK_DEVICE.publish_actuator_status("SW")
            LOOP_COUNTER = 0
        sleep_ms(SLEEP_INTERVAL_MS)
except Exception as e:
    WOLK_DEVICE.disconnect()
    print_exception(e)
