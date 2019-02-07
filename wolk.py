import json


ACTUATOR_STATE_READY = 0
ACTUATOR_STATE_BUSY = 1
ACTUATOR_STATE_ERROR = 2

DEVICE_KEY = None
DEVICE_PASSWORD = None
ACTUATOR_REFERENCES = []
HOST = "api-demo.wolkabout.com"
PORT = 1883


def handle_actuation(reference, value):
    """
    Set actuator to value.

    When the actuation command is given from WolkAbout IoT Platform,
    it will be delivered to this method.
    This method should pass the new value to the device's actuator.
    Must be implemented as non blocking.

    :param reference: Reference of the actuator
    :type reference: str
    :param value: Value to which to set the actuator
    :type value: int or float or str or bool
    """
    pass


def get_actuator_status(reference):
    """
    Get current actuator status.

    Reads the status of actuator from device
    and returns as tuple containing actuator state and current value.
    Must be implemented as non blocking.

    The possible actuator states are:

    - ``wolk.ACTUATOR_STATE_READY``
    - ``wolk.ACTUATOR_STATE_BUSY``
    - ``wolk.ACTUATOR_STATE_ERROR``


    :param reference: Actuator reference
    :type reference: str
    :returns: (state, value)
    :rtype: (wolk.ActuatorState, int or float or str or bool)
    """
    pass


def get_configuration():
    """
    Get current configuration options.

    Reads device configuration options and returns them as a dictionary
    with device configuration reference as key,
    and device configuration value as value.
    Must be implemented as non blocking.


    :returns: configuration
    :rtype: dict
    """
    pass


def handle_configuration(configuration):
    """
    Change device's configuration options.

    This function should update device configuration options
    with received configuration values.

    Must be implemented as thread safe.

    :param configuration: Configuration option reference:value pairs
    :type configuration: dict
    """
    pass


def _make_from_sensor_reading(reference, value, timestamp):
    global DEVICE_KEY
    if isinstance(value, tuple):
        value = ",".join(value)
    if value is True:
        value = "true"
    elif value is False:
        value = "false"
    if "\n" in str(value):
        value = value.replace("\n", "\\n")
    if '"' in str(value):
        value = str(value.replace('"', '\\"'))
        value = str(value.replace('\\\\"', '\\"'))

    if timestamp is None:
        return (
            "readings/" + DEVICE_KEY + "/" + reference,
            '{"data":"' + str(value) + '"}',
        )

    return (
        "readings/" + DEVICE_KEY + "/" + reference,
        '{"data":"' + str(value) + '","utc": ' + str(timestamp) + "}",
    )


def _make_from_alarm(reference, active, timestamp):
    global DEVICE_KEY
    if active is True:
        active = "ON"
    else:
        active = "OFF"
    if timestamp is None:
        return ("events/" + DEVICE_KEY + "/" + reference, '{"data":"' + active + '"}')

    return (
        "events/" + DEVICE_KEY + "/" + reference,
        '{"data":"' + active + '","utc":' + str(timestamp) + "}",
    )


def _make_from_actuator_status(reference, value, state):
    global DEVICE_KEY
    if state == ACTUATOR_STATE_READY:
        state = "READY"
    elif state == ACTUATOR_STATE_BUSY:
        state = "BUSY"
    else:
        state = "ERROR"
    if value is True:
        value = "true"
    elif value is False:
        value = "false"
    if "\n" in str(value):
        value = str(value.replace("\n", "\\n"))
    if '"' in str(value):
        value = str(value.replace('"', '\\"'))
        value = str(value.replace('\\\\"', '\\"'))

    return (
        "actuators/status/" + DEVICE_KEY + "/" + reference,
        '{"status":"' + state + '","value":"' + str(value) + '"}',
    )


def _make_from_keep_alive_message():
    global DEVICE_KEY
    return ("ping/" + DEVICE_KEY, "ping")


def _make_from_configuration(configuration):
    global DEVICE_KEY
    values = str()

    for reference, value in configuration.items():
        if isinstance(value, tuple):
            for single_value in value:
                if single_value is True:
                    single_value = "true"
                elif single_value is False:
                    single_value = "false"
                if "\n" in str(single_value):
                    single_value = str(single_value.replace("\n", "\\n"))
                if '"' in str(single_value):
                    single_value = str(single_value.replace('"', '\\"'))
                    single_value = str(single_value.replace('\\\\"', '\\"'))
            value = ",".join(value)

        if value is True:
            value = "true"
        elif value is False:
            value = "false"

        if "\n" in str(value):
            value = str(value.replace("\n", "\\n"))
        if '"' in str(value):
            value = str(value.replace('"', '\\"'))
            value = str(value.replace('\\\\"', '\\"'))

        values += '"' + reference + '":"' + str(value) + '",'
    values = values[:-1]
    return ("configurations/current/" + DEVICE_KEY, '{"values":{' + values + "}}")


def _deserialize_actuator_command(topic, message):
    topic = topic.decode()
    reference = topic.split("/")[-1]
    payload = json.loads(message)

    value = payload.get("value")
    if "\n" in value:
        value = str(value.replace("\n", "\\n"))
    if value == "true":
        value = True
    elif value == "false":
        value = False
    return (reference, value)


def _deserialize_configuration_command(message):
    payload = json.loads(message)

    configuration = payload.get("values")
    for reference, value in configuration.items():
        if value == "true":
            value = True
        elif value == "false":
            value = False

        if isinstance(value, bool):
            pass
        else:
            if "," in value:
                values_list = value.split(",")
                try:
                    if any("." in value for value in values_list):
                        values_list = [float(value) for value in values_list]
                    else:
                        values_list = [int(value) for value in values_list]
                except ValueError:
                    pass

                configuration[reference] = tuple(values_list)
        return configuration


class WolkConnect:
    def __init__(
        self,
        mqtt_client,
        actuation_handler=None,
        actuator_status_provider=None,
        configuration_handler=None,
        configuration_provider=None,
        storage_size=20,
    ):
        global ACTUATOR_REFERENCES
        self.mqtt_client = mqtt_client
        self.actuation_handler = actuation_handler
        self.actuator_status_provider = actuator_status_provider
        self.configuration_handler = configuration_handler
        self.configuration_provider = configuration_provider

        self.storage_size = storage_size
        self.outbound_message_list = []

        self.mqtt_client.set_callback(self._inbound_message_handler)

        if ACTUATOR_REFERENCES and (
            not actuation_handler or not actuator_status_provider
        ):
            raise RuntimeError(
                "Both a status provider and a handler "
                "must be provided for device with actuators"
            )

    def _inbound_message_handler(self, topic, message):
        if "actuator" in topic:
            reference, value = _deserialize_actuator_command(topic, message)
            if self.actuation_handler:
                self.actuation_handler(reference, value)
                self.publish_actuator_status(reference)

        if "configuration" in topic:
            configuration = _deserialize_configuration_command(message)
            if self.configuration_handler:
                self.configuration_handler(configuration)
                self.publish_configuration()

    def connect(self):
        try:
            global DEVICE_KEY
            global ACTUATOR_REFERENCES
            self.mqtt_client.connect()
            self.mqtt_client.set_last_will("lastwill/" + DEVICE_KEY, "Gone offline")
            if ACTUATOR_REFERENCES:
                topic_root = "actuators/commands/" + DEVICE_KEY + "/"
                for reference in ACTUATOR_REFERENCES:
                    self.mqtt_client.subscribe(topic_root + reference)
            if self.configuration_handler and self.configuration_provider:
                self.mqtt_client.subscribe("configurations/commands/" + DEVICE_KEY)
        except Exception as e:
            raise e

    def disconnect(self):
        global DEVICE_KEY
        self.mqtt_client.publish("lastwill/" + DEVICE_KEY, "Gone offline")
        self.mqtt_client.disconnect()

    def add_sensor_reading(self, reference, value, timestamp=None):
        topic, message = _make_from_sensor_reading(reference, value, timestamp)
        if len(self.outbound_message_list) >= self.storage_size:
            self.outbound_message_list.pop(0)
        self.outbound_message_list.append((topic, message))

    def add_alarm(self, reference, active, timestamp=None):
        topic, message = _make_from_alarm(reference, active, timestamp)
        if len(self.outbound_message_list) >= self.storage_size:
            self.outbound_message_list.pop(0)
        self.outbound_message_list.append((topic, message))

    def publish(self):
        while len(self.outbound_message_list) > 0:
            topic, message = self.outbound_message_list.pop(0)
            self.mqtt_client.publish(topic, message)

    def publish_actuator_status(self, reference):
        if not self.actuation_handler or not self.actuator_status_provider:
            raise RuntimeError("No actuator handler/provider!")
        state, value = self.actuator_status_provider(reference)
        topic, message = _make_from_actuator_status(reference, value, state)
        self.mqtt_client.publish(topic, message)

    def publish_configuration(self):
        if not self.configuration_handler or not self.configuration_provider:
            raise RuntimeError("No configuration handler/provider!")
        configuration = self.configuration_provider()
        topic, message = _make_from_configuration(configuration)

    def send_ping(self):
        topic, message = _make_from_keep_alive_message()
        self.mqtt_client.publish(topic, message)
