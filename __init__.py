ACTUATOR_STATE_READY = 0
ACTUATOR_STATE_BUSY = 1
ACTUATOR_STATE_ERROR = 2

from .wolk import WolkConnect
__all__ = ["WolkConnect"]