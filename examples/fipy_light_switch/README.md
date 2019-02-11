This example controls the state of a lamp by using MikroElektronika's [Relay click](https://www.mikroe.com/relay-click) connected to Pycom's [FiPy](https://pycom.io/product/fipy/) board.

![hackster](https://user-images.githubusercontent.com/34022788/52565680-ce29b780-2e07-11e9-9358-73d961dd4db4.png)

Pycom's [mqtt](https://github.com/pycom/pycom-libraries/blob/master/lib/mqtt/mqtt.py) module is required for this example and it should be copied onto the board under the *flash/lib* directory.
In order to communicate with WolkAbout IoT Platform, the *wolk.py* module from the root of this repository is used and should also be copied onto the board under the *flash/lib* directory.

To run this example, a device must be created on WolkAbout IoT Platform from a *Smart light* device template. This device template can easily be created by importing *Smart light-manifest.json*.
The device credentials received when the device is created should be entered into *example.py* on lines 17 & 18:
```python
wolk.DEVICE_KEY = "device_key"
wolk.DEVICE_PASSWORD = "some_password"
```
The reference used for the light swich should also be entered into the example
```python
wolk.ACTUATOR_REFERENCES = ["SW"]
```

Next, WiFi connection credentials should be entered on lines 22 through 24:
```python
WIFI_SSID = "WIFI_SSID"
WIFI_AUTH = WLAN.WPA2  # WEP, WPA, WPA2, WPA2_ENT
WIFI_PASSWORD = "WIFI_PASSWORD"
```

The pin used to connect the Relay click shold be specified on line 27:
```python
# Relay Click connected on P3 (GPIO4)
LIGHT_SWITCH = Pin("P3", mode=Pin.OUT)
```

After making all these modifications, the *example.py* and *boot.py* files should be copied onto the board under the *flash/* directory.

Pressing the reset button on the board will then result in running the example and the on-board LED will glow a faint red, indicating that the relay has been set into the off state.
Using an actuator widget from the [web application](https://demo.wolkabout.com) or mobile app ([Android](https://play.google.com/store/apps/details?id=com.wolkabout.visualization&hl=en) or [iOS](https://itunes.apple.com/us/app/wolkabout/id1263024064)) will give control over the state of the switch.